# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportAttributeAccessIssue=none, reportGeneralTypeIssues=none
import asyncio
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch
from app.core.authentication.schemas import UserRead
from app.common.crypt import SecurityService
from app.common.storage.postgres import database
from app.core.registration.schemas import PatientCreate
from app.core.registration.services import PatientService
from datetime import date, timedelta
from app.common.storage.redis import redis_client
from app.core.zoom.services import ZoomService
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.common.dependencies import get_current_user
from datetime import datetime, timezone


class TestZoomRoutes(IsolatedAsyncioTestCase):
    async def _cleanup_test_data(self):
        """Helper method to clean up test data"""
        test_names = [("John", "Doe")]
        for first, last in test_names:
            try:
                await PatientService.delete_patient(first, last)
            except Exception:
                pass

    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()
        await redis_client.connect()
        await self._cleanup_test_data()

        self.patient = PatientCreate(
            first_name="John",
            last_name="Doe",
            dob=date(1990, 3, 22),
            province="Ontario",
            disposition="Active",
            referral_site="Toronto",
            age=30,
            gender="Male",
        )
        await PatientService.create_patient(self.patient)
        patients = await PatientService.get_patients()
        self.patient_id = patients[0].id

        # override the dependency
        self.user_id = 1

        async def override_get_current_user():
            return UserRead(
                id=self.user_id,
                email="test@example.com",
                role="admin",
                permissions=[],
                province="Ontario",
                location_permissions=["All"],
                authenticator_mfa_enabled=True,
            )

        app.dependency_overrides[get_current_user] = override_get_current_user

        # Set up HTTP client
        self.client = AsyncClient(
            transport=ASGITransport(app=app), base_url="https://test"
        )

        # Create auth token for test user
        self.user_id = 987
        self.auth_token = await self._get_auth_token(self.user_id)

    async def asyncTearDown(self) -> None:
        app.dependency_overrides.clear()
        await self.client.aclose()

        redis = redis_client.get_client()
        await redis.delete(f"session:metadata:{self.patient_id}")

        await redis_client.disconnect()

        await self._cleanup_test_data()
        await database.disconnect()

    async def _get_auth_token(self, user_id: int) -> str:
        """Helper to create a valid JWT token for testing"""
        token, _ = SecurityService.generate_jwt(
            user_id, timedelta(hours=2), auth=True
        )
        return token

    # DELETE /video/delete/{patient_id}
    async def test_delete_session_successful(self):
        """Host user successfully deletes the session."""
        config = await ZoomService._create_zoom_session(
            self.patient_id, self.user_id
        )

        redis = redis_client.get_client()
        session_dict = await redis.hgetall(
            f"session:metadata:{self.patient_id}"
        )
        last_seen = datetime.fromisoformat(session_dict["host_last_seen_at"])
        now = datetime.now(timezone.utc)

        self.assertEqual(config.host_id, int(session_dict["host_id"]))
        self.assertEqual(config.session_key, session_dict["session_key"])
        self.assertEqual(config.session_name, session_dict["session_name"])
        self.assertEqual("False", session_dict["is_locked"])
        self.assertTrue(last_seen < now)

        # test
        response = await self.client.delete(f"/video/delete/{self.patient_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"message": "Session no longer exists."}
        )

        result = await redis.hgetall(f"session:metadata:{self.patient_id}")
        self.assertEqual(result, {})

    async def test_delete_session_not_host_error(self):
        """Non-host user fails to delete the session."""
        # Create session with a different host
        host_id = 999
        config = await ZoomService._create_zoom_session(
            self.patient_id, host_id
        )

        redis = redis_client.get_client()
        session_dict = await redis.hgetall(
            f"session:metadata:{self.patient_id}"
        )

        # Ensure session exists and current user is NOT host
        self.assertEqual(config.host_id, int(session_dict["host_id"]))
        self.assertNotEqual(self.user_id, int(session_dict["host_id"]))

        # Attempt to delete session as non-host
        response = await self.client.delete(f"/video/delete/{self.patient_id}")

        # Validate response
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["detail"], "User is not the session host"
        )

        # Verify session still exists in Redis
        session_dict_after = await redis.hgetall(
            f"session:metadata:{self.patient_id}"
        )
        self.assertTrue(session_dict_after)
        self.assertEqual(int(session_dict_after["host_id"]), host_id)

    async def test_delete_session_not_found(self):
        """Trying to delete non-existent session returns 404."""
        redis = redis_client.get_client()
        # Ensure Redis does not have session metadata
        await redis.delete(f"session:metadata:{self.patient_id}")
        session_dict = await redis.hgetall(
            f"session:metadata:{self.patient_id}"
        )
        self.assertFalse(session_dict)

        # Attempt to delete session that does not exist
        response = await self.client.delete(f"/video/delete/{self.patient_id}")

        # Validate response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Session not found")

        # Verify Redis still has no session data
        session_dict_after = await redis.hgetall(
            f"session:metadata:{self.patient_id}"
        )
        self.assertFalse(session_dict_after)

    # POST /video/lock/{patient_id}
    async def test_lock_session_successful(self):
        """Host user successfully locks the session."""
        # Create session
        config = await ZoomService._create_zoom_session(
            self.patient_id, self.user_id
        )
        redis = redis_client.get_client()
        session_dict = await redis.hgetall(
            f"session:metadata:{self.patient_id}"
        )

        self.assertEqual(config.host_id, int(session_dict["host_id"]))
        self.assertEqual("False", session_dict["is_locked"])

        # Lock session
        response = await self.client.post(f"/video/lock/{self.patient_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"message": "Session is now locked."}
        )

        # Verify lock in Redis
        session_dict = await redis.hgetall(
            f"session:metadata:{self.patient_id}"
        )
        self.assertEqual(session_dict["is_locked"], "true")

    async def test_lock_session_not_host_error(self):
        """Non-host user fails to lock the session."""
        # Create session with another host
        await ZoomService._create_zoom_session(self.patient_id, 999)
        redis = redis_client.get_client()
        session_dict = await redis.hgetall(
            f"session:metadata:{self.patient_id}"
        )

        self.assertNotEqual(self.user_id, int(session_dict["host_id"]))

        # Attempt to lock
        response = await self.client.post(f"/video/lock/{self.patient_id}")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["detail"], "User is not the session host"
        )

    # POST /video/unlock/{patient_id}
    async def test_unlock_session_successful(self):
        """Host user successfully unlocks the session."""
        await ZoomService._create_zoom_session(self.patient_id, self.user_id)
        redis = redis_client.get_client()
        await ZoomService.lock_session(self.patient_id, self.user_id)

        session_dict = await redis.hgetall(
            f"session:metadata:{self.patient_id}"
        )
        self.assertEqual(session_dict["is_locked"], "true")

        # Unlock session
        response = await self.client.post(f"/video/unlock/{self.patient_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"message": "Session is now unlocked."}
        )

        # Verify lock cleared
        session_dict = await redis.hgetall(
            f"session:metadata:{self.patient_id}"
        )
        self.assertEqual(session_dict["is_locked"], "false")

    async def test_unlock_session_not_host_error(self):
        """Non-host user fails to unlock the session."""
        await ZoomService._create_zoom_session(self.patient_id, 999)
        redis = redis_client.get_client()
        await ZoomService.lock_session(self.patient_id, 999)

        session_dict = await redis.hgetall(
            f"session:metadata:{self.patient_id}"
        )
        self.assertEqual(session_dict["is_locked"], "true")

        # Attempt unlock as non-host
        response = await self.client.post(f"/video/unlock/{self.patient_id}")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["detail"], "User is not the session host"
        )

    # POST /video/join/internal/{patient_id}
    async def test_internal_join_creates_session(self):
        """Internal user joins and creates a new session as host."""
        redis = redis_client.get_client()

        # Ensure no session exists yet
        await redis.delete(f"session:metadata:{self.patient_id}")
        self.assertFalse(
            await redis.exists(f"session:metadata:{self.patient_id}")
        )

        # Internal user joins
        response = await self.client.post(
            f"/video/join/internal/{self.patient_id}"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertIn("expires_at", data)
        self.assertIn("sessionName", data)
        self.assertIn("sessionPasscode", data)
        self.assertTrue(data["sessionName"].startswith(str(self.patient_id)))

        # Check Redis session metadata was created
        session_dict = await redis.hgetall(
            f"session:metadata:{self.patient_id}"
        )
        self.assertTrue(session_dict)
        self.assertEqual(int(session_dict["host_id"]), self.user_id)

    async def test_internal_join_existing_session(self):
        """Internal user joins existing session (not as host)."""
        # Create session with different host
        host_id = 999
        await ZoomService._create_zoom_session(self.patient_id, host_id)

        redis = redis_client.get_client()
        session_dict = await redis.hgetall(
            f"session:metadata:{self.patient_id}"
        )
        self.assertEqual(int(session_dict["host_id"]), host_id)
        self.assertNotEqual(self.user_id, host_id)

        # Internal user joins
        with patch(
            "app.core.zoom.services.ZoomVideoSDKService.get_session",
            return_value=True,
        ):
            response = await self.client.post(
                f"/video/join/internal/{self.patient_id}"
            )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("access_token", data)
        self.assertIn("sessionName", data)
        self.assertEqual(data["sessionName"], session_dict["session_name"])

    async def test_internal_join_locked_session_not_host(self):
        """Internal user denied access to locked session (not host)."""
        # Create session with a different host
        host_id = 999
        await ZoomService._create_zoom_session(self.patient_id, host_id)
        await ZoomService.lock_session(self.patient_id, host_id)

        redis = redis_client.get_client()
        session_dict = await redis.hgetall(
            f"session:metadata:{self.patient_id}"
        )
        self.assertEqual(session_dict["is_locked"], "true")

        # Attempt join as non-host
        with patch(
            "app.core.zoom.services.ZoomVideoSDKService.get_session",
            return_value=True,
        ):
            response = await self.client.post(
                f"/video/join/internal/{self.patient_id}"
            )

        self.assertEqual(response.status_code, 423)
        self.assertIn("locked", response.json()["detail"].lower())

    # POST /video/join/external/{patient_id}
    async def test_external_join_valid_passcode(self):
        """External user joins with valid passcode."""
        await ZoomService._create_zoom_session(self.patient_id, self.user_id)
        redis = redis_client.get_client()
        session_key = await redis.hget(
            f"session:metadata:{self.patient_id}", "session_key"
        )

        with patch(
            "app.core.zoom.services.ZoomVideoSDKService.get_session",
            return_value=True,
        ):
            response = await self.client.post(
                f"/video/join/external/{self.patient_id}",
                json={"passcode": session_key, "guest_id": "guest123"},
            )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("access_token", data)
        self.assertIn("sessionName", data)
        self.assertIn("sessionPasscode", data)

    async def test_external_join_invalid_passcode(self):
        """External user denied access with invalid passcode."""
        await ZoomService._create_zoom_session(self.patient_id, self.user_id)

        with patch(
            "app.core.zoom.services.ZoomVideoSDKService.get_session",
            return_value=True,
        ):
            response = await self.client.post(
                f"/video/join/external/{self.patient_id}",
                json={"passcode": "invalid_key", "guest_id": "guest123"},
            )

        self.assertEqual(response.status_code, 403)
        self.assertIn("passcode", response.json()["detail"].lower())

    async def test_external_join_locked_session(self):
        """External user denied access to locked session."""
        await ZoomService._create_zoom_session(self.patient_id, self.user_id)
        await ZoomService.lock_session(self.patient_id, self.user_id)

        redis = redis_client.get_client()
        session_key = await redis.hget(
            f"session:metadata:{self.patient_id}", "session_key"
        )

        with patch(
            "app.core.zoom.services.ZoomVideoSDKService.get_session",
            return_value=True,
        ):
            response = await self.client.post(
                f"/video/join/external/{self.patient_id}",
                json={"passcode": session_key, "guest_id": "guest123"},
            )

        self.assertEqual(response.status_code, 423)
        self.assertIn("locked", response.json()["detail"].lower())

    async def test_external_join_deleted_session(self):
        """External user denied access to deleted session."""
        await ZoomService._create_zoom_session(self.patient_id, self.user_id)

        redis = redis_client.get_client()
        session_key = await redis.hget(
            f"session:metadata:{self.patient_id}", "session_key"
        )

        # Delete session
        await ZoomService.delete_session(self.patient_id, self.user_id)

        response = await self.client.post(
            f"/video/join/external/{self.patient_id}",
            json={"passcode": session_key, "guest_id": "guest123"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertIn("not active", response.json()["detail"].lower())

    # POST /video/host/poll/{patient_id}
    async def test_refresh_host_lease_success(self):
        """Host can successfully refresh lease via /host/poll endpoint."""
        host_id = self.user_id

        # Create session
        await ZoomService.join_internal(self.patient_id, host_id)

        # Hit the endpoint
        response = await self.client.post(
            f"/video/host/poll/{self.patient_id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Host lease renewed", response.json()["message"])

    async def test_refresh_host_lease_not_host(self):
        """Non-host cannot refresh lease via /host/poll endpoint."""
        await ZoomService._create_zoom_session(self.patient_id, 999)

        # Simulate a different user making the request
        response = await self.client.post(
            f"/video/host/poll/{self.patient_id}",
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn(
            "not the session host", response.json()["detail"].lower()
        )

    async def test_refresh_host_lease_expired(self):
        """Refreshing a host lease after session is expired returns 410."""
        host_id = self.user_id
        # Create session
        await ZoomService.join_internal(self.patient_id, host_id)

        # Expire the session
        redis = redis_client.get_client()
        past_time = datetime.now(timezone.utc) - timedelta(minutes=10)
        await redis.hset(
            f"session:metadata:{self.patient_id}",
            "host_last_seen_at",
            past_time.isoformat(),
        )

        response = await self.client.post(
            f"/video/host/poll/{self.patient_id}"
        )

        self.assertEqual(response.status_code, 410)
        self.assertIn("expired", response.json()["detail"].lower())

    async def test_refresh_host_lease_nonexistent_session(self):
        """Refreshing a lease on a non-existent session returns 404."""
        # Ensure session does not exist
        redis = redis_client.get_client()
        await redis.delete(f"session:metadata:{self.patient_id}")

        response = await self.client.post(
            f"/video/host/poll/{self.patient_id}"
        )

        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json()["detail"].lower())
