# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportAttributeAccessIssue=none
import asyncio
from datetime import datetime, timedelta, timezone
from unittest import IsolatedAsyncioTestCase
from datetime import date
from app.database import database, redis_client
from app.registration.schemas import PatientCreate
from app.registration.services import PatientService
from app.exceptions import (
    NotFoundError,
    ForbiddenError,
    SessionExpiredError,
    SessionLockedError,
)
from app.zoom.services import ZoomService


class TestZoomService(IsolatedAsyncioTestCase):
    async def _cleanup_test_data(self):
        """Helper method to clean up test patients"""
        test_names = [("John", "Doe")]
        for first, last in test_names:
            try:
                await PatientService.delete_patient(first, last)
            except Exception:
                pass

    async def asyncSetUp(self):
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

    async def asyncTearDown(self):
        await self._cleanup_test_data()
        redis = redis_client.get_client()
        await redis.delete(f"session:metadata:{self.patient_id}")
        await database.disconnect()
        await redis_client.disconnect()

    # ----------------------
    # Internal join
    # ----------------------
    async def test_join_internal_success_host(self):
        """User becomes host on new session."""
        user_id = 1001
        result = await ZoomService.join_internal(self.patient_id, user_id)
        last_seen = datetime.fromisoformat(result["host_last_seen_at"])
        now = datetime.now(timezone.utc)

        self.assertEqual(result["host_id"], user_id)
        self.assertIn(str(self.patient_id), result["session_name"])
        self.assertFalse(result["is_locked"])
        self.assertNotEqual(result["session_key"], "")
        self.assertTrue((now - last_seen) < timedelta(seconds=1))

        redis = redis_client.get_client()
        cached = await redis.hgetall(f"session:metadata:{self.patient_id}")
        self.assertEqual(int(cached["host_id"]), user_id)
        self.assertEqual(cached["session_name"], result["session_name"])

    async def test_join_internal_existing_not_host(self):
        """User joins existing session as non-host."""
        host_id = 1002
        result = await ZoomService.join_internal(self.patient_id, host_id)
        last_seen = datetime.fromisoformat(result["host_last_seen_at"])

        new_user_id = 2002
        result = await ZoomService.join_internal(self.patient_id, new_user_id)
        last_seen2 = datetime.fromisoformat(result["host_last_seen_at"])

        self.assertEqual(int(result["host_id"]), host_id)
        self.assertNotEqual(result["host_id"], new_user_id)
        self.assertEqual(last_seen, last_seen2)

    async def test_join_internal_success_host_again(self):
        """User becomes host on new session."""
        user_id = 1001
        result = await ZoomService.join_internal(self.patient_id, user_id)
        last_seen = datetime.fromisoformat(result["host_last_seen_at"])

        result2 = await ZoomService.join_internal(self.patient_id, user_id)

        redis = redis_client.get_client()
        data = await redis.hgetall(f"session:metadata:{self.patient_id}")
        data_dict = dict(data)
        last_seen2 = datetime.fromisoformat(data_dict["host_last_seen_at"])

        self.assertEqual(result["host_id"], result2["host_id"])
        self.assertEqual(result["session_name"], result2["session_name"])
        self.assertEqual(result["is_locked"], result2["is_locked"])
        self.assertEqual(result["session_key"], result2["session_key"])
        self.assertTrue(last_seen < last_seen2)

    async def test_join_internal_locked_not_host(self):
        """Non-host denied when session is locked."""
        host_id = 1003
        await ZoomService.join_internal(self.patient_id, host_id)
        await ZoomService.lock_session(self.patient_id, host_id)

        with self.assertRaises(SessionLockedError):
            await ZoomService.join_internal(self.patient_id, 3003)

    async def test_join_internal_cache_stale(self):
        """Internal join recreates session if Zoom session no longer exists."""
        host_id = 1004
        session = await ZoomService.join_internal(self.patient_id, host_id)

        # Simulate stale cache (Zoom session gone)
        redis = redis_client.get_client()
        past_time = datetime.now(timezone.utc) - timedelta(minutes=3)

        await redis.hset(
            f"session:metadata:{self.patient_id}",
            "host_last_seen_at",
            past_time.isoformat(),
        )

        new_result = await ZoomService.join_internal(self.patient_id, host_id)

        self.assertIn(str(self.patient_id), new_result["session_name"])
        self.assertNotEqual(
            new_result["session_name"], session["session_name"]
        )
        self.assertNotEqual(new_result["session_key"], session["session_key"])
        self.assertEqual(new_result["host_id"], session["host_id"])

    # ----------------------
    # External join
    # ----------------------
    async def test_join_external_success(self):
        """External user joins with correct passcode."""
        host_id = 1010
        await ZoomService.join_internal(self.patient_id, host_id)

        redis = redis_client.get_client()
        session_key = await redis.hget(
            f"session:metadata:{self.patient_id}", "session_key"
        )

        result = await ZoomService.join_external(self.patient_id, session_key)

        self.assertEqual(int(result["host_id"]), host_id)
        self.assertEqual(result["session_key"], session_key)

    async def test_join_external_invalid_passcode(self):
        """External user denied for wrong passcode."""
        host_id = 1011
        await ZoomService.join_internal(self.patient_id, host_id)

        with self.assertRaises(ForbiddenError):
            await ZoomService.join_external(self.patient_id, "wrong_key")

    async def test_join_external_locked(self):
        """External denied if session locked."""
        host_id = 1012
        await ZoomService.join_internal(self.patient_id, host_id)
        await ZoomService.lock_session(self.patient_id, host_id)

        redis = redis_client.get_client()
        session_key = await redis.hget(
            f"session:metadata:{self.patient_id}", "session_key"
        )

        with self.assertRaises(SessionLockedError):
            await ZoomService.join_external(self.patient_id, session_key)

    async def test_join_external_stale(self):
        """External denied if session locked."""
        host_id = 1012
        await ZoomService.join_internal(self.patient_id, host_id)

        # Simulate stale cache (Zoom session gone)
        redis = redis_client.get_client()
        past_time = datetime.now(timezone.utc) - timedelta(minutes=3)

        await redis.hset(
            f"session:metadata:{self.patient_id}",
            "host_last_seen_at",
            past_time.isoformat(),
        )

        # redis = redis_client.get_client()
        session_key = await redis.hget(
            f"session:metadata:{self.patient_id}", "session_key"
        )

        with self.assertRaises(NotFoundError):
            await ZoomService.join_external(self.patient_id, session_key)

    async def test_join_external_zoom_session_missing(self):
        """External join fails if Zoom session no longer exists."""
        with self.assertRaises(NotFoundError):
            await ZoomService.join_external(self.patient_id, "key")

    # ----------------------
    # Lock / Unlock
    # ----------------------
    async def test_lock_unlock_success(self):
        """Host can lock and unlock session."""
        host_id = 1020
        await ZoomService.join_internal(self.patient_id, host_id)

        # Lock
        await ZoomService.lock_session(self.patient_id, host_id)
        locked = await ZoomService._check_lock(self.patient_id)
        self.assertTrue(locked)

        # Unlock
        await ZoomService.unlock_session(self.patient_id, host_id)
        locked = await ZoomService._check_lock(self.patient_id)
        self.assertFalse(locked)

    async def test_lock_not_host(self):
        """Non-host cannot lock session."""
        host_id = 1021
        await ZoomService.join_internal(self.patient_id, host_id)

        with self.assertRaises(ForbiddenError):
            await ZoomService.lock_session(self.patient_id, 9999)

    async def test_unlock_not_host(self):
        """Non-host cannot unlock session."""
        host_id = 1022
        await ZoomService.join_internal(self.patient_id, host_id)
        await ZoomService.lock_session(self.patient_id, host_id)

        with self.assertRaises(ForbiddenError):
            await ZoomService.unlock_session(self.patient_id, 9999)

    # ----------------------
    # Delete session
    # ----------------------
    async def test_delete_session_success(self):
        """Host can delete session."""
        host_id = 1030
        await ZoomService.join_internal(self.patient_id, host_id)

        await ZoomService.delete_session(self.patient_id, host_id)

        redis = redis_client.get_client()
        data = await redis.hgetall(f"session:metadata:{self.patient_id}")
        self.assertFalse(data)

    async def test_delete_not_host(self):
        """Non-host cannot delete session."""
        host_id = 1031
        await ZoomService.join_internal(self.patient_id, host_id)

        with self.assertRaises(ForbiddenError):
            await ZoomService.delete_session(self.patient_id, 9999)

    async def test_delete_nonexistent_session(self):
        """Deleting nonexistent session raises NotFoundError."""
        with self.assertRaises(NotFoundError):
            await ZoomService.delete_session(self.patient_id, 1234)

    # ----------------------
    # Refresh host lease
    # ----------------------
    async def test_refresh_host_lease_success(self):
        """Host can successfully refresh lease."""
        host_id = 2001
        # Create session
        await ZoomService.join_internal(self.patient_id, host_id)

        # Get previous last_seen
        redis = redis_client.get_client()
        before = await redis.hget(
            f"session:metadata:{self.patient_id}", "host_last_seen_at"
        )

        await ZoomService.refresh_host_lease(self.patient_id, host_id)

        after = await redis.hget(
            f"session:metadata:{self.patient_id}", "host_last_seen_at"
        )

        self.assertNotEqual(before, after)  # timestamp updated

    async def test_refresh_host_lease_nonexistent(self):
        """Refreshing lease on non-existent session raises NotFoundError."""
        with self.assertRaises(NotFoundError):
            await ZoomService.refresh_host_lease(self.patient_id, 9999)

    async def test_refresh_host_lease_not_host(self):
        """Non-host cannot refresh lease."""
        host_id = 2002
        non_host_id = 8888
        await ZoomService.join_internal(self.patient_id, host_id)

        with self.assertRaises(ForbiddenError):
            await ZoomService.refresh_host_lease(self.patient_id, non_host_id)

    async def test_refresh_host_lease_stale(self):
        """Refreshing a stale session behaves correctly (host timeout)."""
        host_id = 2003
        await ZoomService.join_internal(self.patient_id, host_id)

        # Set host_last_seen_at to past (simulate stale)
        redis = redis_client.get_client()
        past_time = datetime.now(timezone.utc) - timedelta(minutes=10)
        await redis.hset(
            f"session:metadata:{self.patient_id}",
            "host_last_seen_at",
            past_time.isoformat(),
        )

        with self.assertRaises(SessionExpiredError):
            await ZoomService.refresh_host_lease(self.patient_id, host_id)

        updated = await redis.hget(
            f"session:metadata:{self.patient_id}", "host_last_seen_at"
        )
        self.assertEqual(past_time.isoformat(), updated)
