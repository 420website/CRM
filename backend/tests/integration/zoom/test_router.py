# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportAttributeAccessIssue=none
import asyncio
from unittest import IsolatedAsyncioTestCase
from app.authentication.schemas import UserRead
from app.authentication.utils import SecurityService
from app.database import database
from app.registration.schemas import PatientCreate
from app.registration.services import PatientService
from datetime import date, timedelta
from app.database import redis_client
from app.zoom.schema import SessionConfig
from app.zoom.services import ZoomService
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.dependencies import get_current_user


async def create_session(user_id: int, patient_id: int):
    async with database.get_transaction() as conn:
        # Create new session with user as host
        config = SessionConfig(
            patient_id=patient_id,
            session_name=f"{patient_id}-{SecurityService.generate_secure_token(4)}",
            session_key=SecurityService.generate_secure_token(8),
            host_id=user_id,
            is_locked=False,
            locked_at=None,
            is_deleted=False,
            deleted_at=None,
            created_at=None,
        )
        session_dict = await ZoomService._upsert_session(conn, config)
        session_config = SessionConfig(**session_dict).encode()

    # Cache result
    try:
        redis = redis_client.get_client()
        await redis.hset(
            f"session:config:{patient_id}", mapping=session_config
        )
    except Exception as e:
        raise Exception(f"Failed to cache session {patient_id}: {e}")


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
        await redis.delete(f"session:config:{self.patient_id}")
        await redis.delete(f"session:{self.patient_id}:is_locked")
        await redis.delete(f"session:participants:{self.patient_id}")

        await redis_client.disconnect()

        await self._cleanup_test_data()
        await database.disconnect()

    async def _get_auth_token(self, user_id: int) -> str:
        """Helper to create a valid JWT token for testing"""
        (token, _) = SecurityService.generate_jwt(
            user_id, timedelta(hours=2), auth=True
        )
        return token

    # DELETE /video/delete/{patient_id}
    async def test_delete_session_successful(self):
        """Host user successfully deletes the session."""
        await create_session(self.user_id, self.patient_id)

        response = await self.client.delete(f"/video/delete/{self.patient_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"message": "Session no longer exists."}
        )

    async def test_delete_session_not_host_error(self):
        """Non-host user fails to delete the session."""
        await create_session(99, self.patient_id)

        response = await self.client.delete(f"/video/delete/{self.patient_id}")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["detail"], "User is not the session host"
        )

    async def test_delete_session_not_found(self):
        """Trying to delete non-existent session returns 404."""
        response = await self.client.delete(f"/video/delete/{self.patient_id}")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Session not found")

    # POST /video/lock/{patient_id}
    async def test_lock_session_successful(self):
        """Host user successfully locks the session."""
        await create_session(self.user_id, self.patient_id)

        response = await self.client.post(f"/video/lock/{self.patient_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"message": "Session is now locked."}
        )

    async def test_lock_session_not_host_error(self):
        """Non-host user fails to lock the session."""
        await create_session(99, self.patient_id)

        response = await self.client.post(f"/video/lock/{self.patient_id}")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["detail"], "User is not the session host"
        )

    async def test_lock_session_not_found(self):
        """Trying to lock non-existent session returns 404."""
        response = await self.client.post(f"/video/lock/{self.patient_id}")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Session not found")

    # POST /video/unlock/{patient_id}
    async def test_unlock_session_successful(self):
        """Host user successfully unlocks the session."""
        await create_session(self.user_id, self.patient_id)
        await ZoomService.lock_session(self.patient_id, self.user_id)

        response = await self.client.post(f"/video/unlock/{self.patient_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"message": "Session is now unlocked."}
        )

    async def test_unlock_session_not_host_error(self):
        """Non-host user fails to unlock the session."""
        await create_session(99, self.patient_id)
        await ZoomService.lock_session(self.patient_id, 99)

        response = await self.client.post(f"/video/unlock/{self.patient_id}")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["detail"], "User is not the session host"
        )

    async def test_unlock_session_not_found(self):
        """Trying to unlock non-existent session returns 404."""
        response = await self.client.post(f"/video/unlock/{self.patient_id}")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Session not found")

    # POST /video/join/internal/{patient_id}
    async def test_internal_join_creates_session(self):
        """Internal user joins and creates a new session as host."""
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

    async def test_internal_join_existing_session(self):
        """Internal user joins existing session (not as host)."""
        await create_session(99, self.patient_id)

        response = await self.client.post(
            f"/video/join/internal/{self.patient_id}"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertIn("sessionName", data)

    async def test_internal_join_locked_session_not_host(self):
        """Internal user denied access to locked session (not host)."""
        await create_session(99, self.patient_id)
        await ZoomService.lock_session(self.patient_id, 99)

        response = await self.client.post(
            f"/video/join/internal/{self.patient_id}"
        )

        self.assertEqual(response.status_code, 423)
        self.assertIn("locked", response.json()["detail"].lower())

    # POST /video/join/external/{patient_id}
    async def test_external_join_valid_passcode(self):
        """External user joins with valid passcode."""
        await create_session(self.user_id, self.patient_id)
        redis = redis_client.get_client()
        session_key = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )

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
        await create_session(self.user_id, self.patient_id)

        response = await self.client.post(
            f"/video/join/external/{self.patient_id}",
            json={"passcode": "invalid_key", "guest_id": "guest123"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn("passcode", response.json()["detail"].lower())

    async def test_external_join_locked_session(self):
        """External user denied access to locked session."""
        await create_session(self.user_id, self.patient_id)
        await ZoomService.lock_session(self.patient_id, self.user_id)
        redis = redis_client.get_client()
        session_key = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )

        response = await self.client.post(
            f"/video/join/external/{self.patient_id}",
            json={"passcode": session_key, "guest_id": "guest123"},
        )

        self.assertEqual(response.status_code, 423)
        self.assertIn("locked", response.json()["detail"].lower())

    async def test_external_join_deleted_session(self):
        """External user denied access to deleted session."""
        await create_session(self.user_id, self.patient_id)
        redis = redis_client.get_client()
        session_key = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )
        await ZoomService.delete_session(self.patient_id, self.user_id)

        response = await self.client.post(
            f"/video/join/external/{self.patient_id}",
            json={"passcode": session_key, "guest_id": "guest123"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn("passcode", response.json()["detail"].lower())

    # POST /video/sync/{patient_id}
    async def test_sync_participants_successful(self):
        """Successfully sync participants list."""
        await create_session(self.user_id, self.patient_id)
        redis = redis_client.get_client()
        session_key = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )

        response = await self.client.post(
            f"/video/sync/{self.patient_id}",
            json={
                "session_key": session_key,
                "zoom_participants": [str(self.user_id), "123"],
            },
        )

        self.assertEqual(response.status_code, 200)

        # Verify participants were synced
        participants = list(
            await redis.smembers(f"session:participants:{self.patient_id}")
        )
        self.assertEqual(len(participants), 2)

    async def test_sync_participants_clears_session(self):
        """Syncing with empty list deletes the session."""
        await create_session(self.user_id, self.patient_id)
        redis = redis_client.get_client()
        session_key = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )

        response = await self.client.post(
            f"/video/sync/{self.patient_id}",
            json={"session_key": session_key, "zoom_participants": []},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "Session deleted.")

        # Verify session cleared
        isConfig = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )
        self.assertFalse(isConfig)

        async with database.get_connection() as conn:
            result = await ZoomService._get_session(conn, self.patient_id)
            self.assertIsNone(result)

    async def test_sync_participants_invalid_passcode(self):
        """Sync with invalid passcode returns 403."""
        await create_session(self.user_id, self.patient_id)

        response = await self.client.post(
            f"/video/sync/{self.patient_id}",
            json={"session_key": "invalid_key", "zoom_participants": []},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Invalid passcode")

    async def test_sync_participants_with_lock(self):
        """Syncing empty list clears lock."""
        await create_session(self.user_id, self.patient_id)
        redis = redis_client.get_client()

        # Set lock
        await redis.set(f"session:{self.patient_id}:is_locked", "true")

        session_key = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )

        response = await self.client.post(
            f"/video/sync/{self.patient_id}",
            json={"session_key": session_key, "zoom_participants": []},
        )

        self.assertEqual(response.status_code, 200)

        # Verify lock cleared
        isLock = await redis.get(f"session:{self.patient_id}:is_locked")
        self.assertFalse(isLock)

    async def test_sync_participants_already_deleted(self):
        """Syncing already deleted session returns error."""
        await create_session(self.user_id, self.patient_id)
        redis = redis_client.get_client()
        session_key = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )

        # Delete first time
        await self.client.post(
            f"/video/sync/{self.patient_id}",
            json={"session_key": session_key, "zoom_participants": []},
        )

        # Try again
        response = await self.client.post(
            f"/video/sync/{self.patient_id}",
            json={"session_key": session_key, "zoom_participants": []},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Invalid passcode")

    async def test_sync_multiple_participants(self):
        """Syncing multiple participants works correctly."""
        await create_session(self.user_id, self.patient_id)
        redis = redis_client.get_client()
        session_key = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )

        participants = ["1", "2", "3", "4"]
        response = await self.client.post(
            f"/video/sync/{self.patient_id}",
            json={
                "session_key": session_key,
                "zoom_participants": participants,
            },
        )

        self.assertEqual(response.status_code, 200)

        # Verify all participants synced
        synced = list(
            await redis.smembers(f"session:participants:{self.patient_id}")
        )
        self.assertEqual(len(synced), 4)

    async def test_sync_participants_no_session(self):
        """Syncing when no session exists returns error."""
        response = await self.client.post(
            f"/video/sync/{self.patient_id}",
            json={"session_key": "nonexistent", "zoom_participants": ["1"]},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Invalid passcode")
