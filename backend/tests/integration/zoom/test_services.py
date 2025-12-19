# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportAttributeAccessIssue=none
import asyncio
from unittest import IsolatedAsyncioTestCase
from app.authentication.utils import SecurityService
from app.database import database
from app.exceptions import APIError
from app.registration.schemas import PatientCreate
from app.registration.services import PatientService
from datetime import date
from app.database import redis_client
from app.zoom.schema import SessionConfig
from app.zoom.services import ZoomService


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


class TestZoomService(IsolatedAsyncioTestCase):
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

    async def asyncTearDown(self) -> None:
        await self._cleanup_test_data()
        redis = redis_client.get_client()
        await redis.delete(f"session:config:{self.patient_id}")
        await redis.delete(f"session:{self.patient_id}:is_locked")
        await redis.delete(f"session:participants:{self.patient_id}")

        await redis_client.disconnect()
        await database.disconnect()

    # delete
    async def test_delete_session_sucessfully(self):
        """Delete a session as host in DB and Cache"""
        user_id = 987
        await create_session(user_id, self.patient_id)

        # validate creation
        async with database.get_connection() as conn:
            result = await ZoomService._get_session(conn, self.patient_id)
            self.assertIsNotNone(result)

        redis = redis_client.get_client()
        result = await redis.hgetall(f"session:config:{self.patient_id}")
        self.assertIsNotNone(result)

        # test
        await ZoomService.delete_session(self.patient_id, user_id)

        # Validate
        async with database.get_connection() as conn:
            result = await ZoomService._get_session(conn, self.patient_id)
            self.assertIsNone(result)

        redis = redis_client.get_client()
        result = await redis.hgetall(f"session:config:{self.patient_id}")
        self.assertFalse(result)

        result = await redis.get(f"session:{self.patient_id}:is_locked")
        self.assertFalse(result)

    async def test_delete_locked_session_sucessfully(self):
        """Delete a session as host that is currently locked. The lock and session should be cleaned up."""
        user_id = 987
        await create_session(user_id, self.patient_id)
        await ZoomService.lock_session(self.patient_id, user_id)

        # validate creation
        async with database.get_connection() as conn:
            result = await ZoomService._get_session(conn, self.patient_id)
            self.assertIsNotNone(result)

        redis = redis_client.get_client()
        result = await redis.hgetall(f"session:config:{self.patient_id}")
        self.assertIsNotNone(result)

        result = await redis.get(f"session:{self.patient_id}:is_locked")
        self.assertTrue(result)

        # test
        await ZoomService.delete_session(self.patient_id, user_id)

        # Validate
        async with database.get_connection() as conn:
            result = await ZoomService._get_session(conn, self.patient_id)
            self.assertIsNone(result)

        redis = redis_client.get_client()
        result = await redis.hgetall(f"session:config:{self.patient_id}")
        self.assertFalse(result)

        result = await redis.get(f"session:{self.patient_id}:is_locked")
        self.assertFalse(result)

    async def test_delete_session_not_in_cache(self):
        """Delete session sucessfully from DB, not found in cache. Cache deletes proceed if not found."""
        redis = redis_client.get_client()

        user_id = 987
        await create_session(user_id, self.patient_id)
        await redis.delete(f"session:config:{self.patient_id}")

        # test
        await ZoomService.delete_session(self.patient_id, user_id)

        # validate
        async with database.get_connection() as conn:
            result = await ZoomService._get_session(conn, self.patient_id)
            self.assertIsNone(result)

        result = await redis.hgetall(f"session:config:{self.patient_id}")
        self.assertIsNotNone(result)

    async def test_delete_session_doesnt_exist(self):
        """Trying to delete a session that is already deleted returns an APIError."""
        user_id = 987

        await create_session(user_id, self.patient_id)
        await ZoomService.delete_session(self.patient_id, user_id)

        # test
        with self.assertRaises(APIError) as error:
            await ZoomService.delete_session(self.patient_id, user_id)

        self.assertEqual(str(error.exception), "Session not found")

    async def test_delete_session_not_in_db(self):
        """Trying to delete a session that doesnt exist at all in the DB."""
        user_id = 987

        # test
        with self.assertRaises(APIError) as error:
            await ZoomService.delete_session(self.patient_id, user_id)

        self.assertEqual(str(error.exception), "Session not found")

    async def test_delete_session_not_host(self):
        """Deleting as not host, returns an APIError. DB and Cache unchanged."""
        user_id = 987
        await create_session(user_id, self.patient_id)

        # test
        with self.assertRaises(APIError) as error:
            await ZoomService.delete_session(self.patient_id, -1)

        self.assertEqual(
            str(error.exception),
            "User is not the session host",
        )

        # validate
        async with database.get_connection() as conn:
            result = await ZoomService._get_session(conn, self.patient_id)
            self.assertIsNotNone(result)

        redis = redis_client.get_client()
        result = await redis.hgetall(f"session:config:{self.patient_id}")
        self.assertIsNotNone(result)

    # lock
    async def test_lock_session_sucessfully(self):
        """Successfully lock a session as host, DB and Cache updated."""
        user_id = 987
        await create_session(user_id, self.patient_id)

        # validate creation
        async with database.get_connection() as conn:
            result = await ZoomService._check_lock(conn, self.patient_id)
            self.assertFalse(result)

        redis = redis_client.get_client()
        result = await redis.get(f"session:{self.patient_id}:is_locked")
        self.assertFalse(result)

        # test
        await ZoomService.lock_session(self.patient_id, user_id)

        # Validate
        async with database.get_connection() as conn:
            result = await ZoomService._check_lock(conn, self.patient_id)
            self.assertTrue(result)

        redis = redis_client.get_client()
        result = await redis.get(f"session:{self.patient_id}:is_locked")
        self.assertTrue(result)

    async def test_lock_not_host(self):
        """Failed to lock session because not host. DB and Cache show unlocked."""
        user_id = 987
        await create_session(user_id, self.patient_id)

        # test
        with self.assertRaises(APIError) as err:
            await ZoomService.lock_session(self.patient_id, -1)

        self.assertEqual(str(err.exception), "User is not the session host")

        # Validate
        async with database.get_connection() as conn:
            result = await ZoomService._check_lock(conn, self.patient_id)
            self.assertFalse(result)

        redis = redis_client.get_client()
        result = await redis.get(f"session:{self.patient_id}:is_locked")
        self.assertFalse(result)

    # unlock
    async def test_unlock_session_sucessfully(self):
        """Sucessfully unlock the session as the host."""
        user_id = 987
        await create_session(user_id, self.patient_id)
        await ZoomService.lock_session(self.patient_id, user_id)

        # validate creation
        async with database.get_connection() as conn:
            result = await ZoomService._check_lock(conn, self.patient_id)
            self.assertTrue(result)

        redis = redis_client.get_client()
        result = await redis.get(f"session:{self.patient_id}:is_locked")
        self.assertTrue(result)

        # test
        await ZoomService.unlock_session(self.patient_id, user_id)

        # Validate
        async with database.get_connection() as conn:
            result = await ZoomService._check_lock(conn, self.patient_id)
            self.assertFalse(result)

        redis = redis_client.get_client()
        result = await redis.get(f"session:{self.patient_id}:is_locked")
        self.assertEqual(result, "false")

    async def test_unlock_session_not_host(self):
        """Failed to unlock session because the user is not host."""
        user_id = 987
        await create_session(user_id, self.patient_id)
        await ZoomService.lock_session(self.patient_id, user_id)

        # test
        with self.assertRaises(APIError) as err:
            await ZoomService.unlock_session(self.patient_id, -1)

        self.assertEqual(str(err.exception), "User is not the session host")

        # Validate
        async with database.get_connection() as conn:
            result = await ZoomService._check_lock(conn, self.patient_id)
            self.assertTrue(result)

        redis = redis_client.get_client()
        result = await redis.get(f"session:{self.patient_id}:is_locked")
        self.assertEqual(result, "true")

    # join internal session
    async def test_join_internal_success(self):
        """Successfully create a session as one does not exists, user made host."""
        user_id = 989

        # Test
        result = await ZoomService.join_internal(self.patient_id, user_id)

        # Validate
        self.assertEqual(result["patient_id"], self.patient_id)
        self.assertEqual(
            result["session_name"].split("-")[0], str(self.patient_id)
        )
        self.assertNotEqual(result["session_key"], "")
        self.assertEqual(result["host_id"], user_id)
        self.assertEqual(result["is_locked"], False)
        self.assertEqual(result["locked_at"], None)
        self.assertEqual(result["is_deleted"], False)
        self.assertEqual(result["deleted_at"], None)
        self.assertEqual(result["created_at"], None)

        redis = redis_client.get_client()
        cached_config = await redis.hgetall(
            f"session:config:{self.patient_id}"
        )

        self.assertEqual(
            result["patient_id"], int(cached_config["patient_id"])
        )
        self.assertEqual(cached_config["session_name"], result["session_name"])
        self.assertEqual(result["session_key"], cached_config["session_key"])
        self.assertEqual(result["host_id"], int(cached_config["host_id"]))
        self.assertEqual(str(result["is_locked"]), cached_config["is_locked"])
        self.assertEqual(
            str(result["is_deleted"]), cached_config["is_deleted"]
        )

    async def test_join_internal_success_not_host(self):
        """Successfully joins a session not as host because one already exists."""
        user_id = 989
        await create_session(user_id, self.patient_id)

        # Test
        result = await ZoomService.join_internal(self.patient_id, 1787)

        # Validate
        self.assertEqual(result["patient_id"], self.patient_id)
        self.assertEqual(
            result["session_name"].split("-")[0], str(self.patient_id)
        )
        self.assertNotEqual(result["session_key"], "")
        self.assertEqual(result["host_id"], user_id)
        self.assertEqual(result["is_locked"], False)
        self.assertEqual(result["locked_at"], None)
        self.assertEqual(result["is_deleted"], False)
        self.assertEqual(result["deleted_at"], None)
        self.assertEqual(result["created_at"], None)

        redis = redis_client.get_client()
        cached_config = await redis.hgetall(
            f"session:config:{self.patient_id}"
        )
        self.assertEqual(
            result["patient_id"], int(cached_config["patient_id"])
        )
        self.assertEqual(cached_config["session_name"], result["session_name"])
        self.assertEqual(result["session_key"], cached_config["session_key"])
        self.assertEqual(result["host_id"], int(cached_config["host_id"]))
        self.assertEqual(str(result["is_locked"]), cached_config["is_locked"])
        self.assertEqual(
            str(result["is_deleted"]), cached_config["is_deleted"]
        )

    async def test_join_locked_session_not_host(self):
        """Denied access to the session because not the host."""
        user_id = 989
        await create_session(user_id, self.patient_id)
        await ZoomService.lock_session(self.patient_id, user_id)

        # Test
        with self.assertRaises(APIError) as err:
            await ZoomService.join_internal(self.patient_id, 1787)

        self.assertEqual(str(err.exception), "Session is locked.")

    async def test_join_locked_session_not_host_cache_stale(self):
        """
        Cache returning unlocked checks database to confirm, and returns error because database has locked.
        Cache is then updated to reflect database state.
        """
        user_id = 989
        await create_session(user_id, self.patient_id)
        await ZoomService.lock_session(self.patient_id, user_id)

        redis = redis_client.get_client()
        await redis.set(f"session:config:{self.patient_id}", "false")

        # Test
        with self.assertRaises(APIError) as err:
            await ZoomService.join_internal(self.patient_id, 1787)

        self.assertEqual(str(err.exception), "Session is locked.")

        cached_lock = await redis.get(f"session:{self.patient_id}:is_locked")
        self.assertEqual(cached_lock, "true")

    # join internal session
    async def test_join_external_success(self):
        """External user successfully joins session not as a guest."""
        user_id = 979
        await create_session(user_id, self.patient_id)
        redis = redis_client.get_client()
        session_key = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )

        # Test
        result = await ZoomService.join_external(self.patient_id, session_key)

        # Validate
        self.assertEqual(result["patient_id"], self.patient_id)
        self.assertEqual(
            result["session_name"].split("-")[0], str(self.patient_id)
        )
        self.assertNotEqual(result["session_key"], "")
        self.assertEqual(result["host_id"], user_id)
        self.assertEqual(result["is_locked"], False)
        self.assertEqual(result["locked_at"], None)
        self.assertEqual(result["is_deleted"], False)
        self.assertEqual(result["deleted_at"], None)
        self.assertEqual(result["created_at"], None)

        redis = redis_client.get_client()
        cached_config = await redis.hgetall(
            f"session:config:{self.patient_id}"
        )
        self.assertEqual(
            result["patient_id"], int(cached_config["patient_id"])
        )
        self.assertEqual(cached_config["session_name"], result["session_name"])
        self.assertEqual(result["session_key"], cached_config["session_key"])
        self.assertEqual(result["host_id"], int(cached_config["host_id"]))
        self.assertEqual(str(result["is_locked"]), cached_config["is_locked"])
        self.assertEqual(
            str(result["is_deleted"]), cached_config["is_deleted"]
        )

    async def test_join_external_invalid_cache(self):
        """External user denied access due to invalid passcode."""
        user_id = 979
        await create_session(user_id, self.patient_id)

        # Test
        with self.assertRaises(APIError) as err:
            await ZoomService.join_external(self.patient_id, "invalid")

        self.assertEqual(str(err.exception), "Invalid passcode.")

    async def test_join_external_invalid_database(self):
        """External user denied access because the database session_key is different. Even though the cach validated."""
        redis = redis_client.get_client()

        user_id = 979
        await create_session(user_id, self.patient_id)
        await redis.hset(
            f"session:config:{self.patient_id}",
            "session_key",
            "invalid",
        )

        # Test
        with self.assertRaises(APIError) as err:
            await ZoomService.join_external(self.patient_id, "invalid")

        self.assertEqual(str(err.exception), "Invalid passcode.")

    async def test_join_external_locked_cache(self):
        """External user denied access because the session is locked."""
        user_id = 979
        await create_session(user_id, self.patient_id)
        await ZoomService.lock_session(self.patient_id, user_id)
        redis = redis_client.get_client()
        session_key = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )

        # Test
        with self.assertRaises(APIError) as err:
            await ZoomService.join_external(self.patient_id, session_key)

        self.assertEqual(str(err.exception), "Session is locked.")

    async def test_join_external_locked_database(self):
        """External user denied access because the session is locked."""
        redis = redis_client.get_client()

        user_id = 979
        await create_session(user_id, self.patient_id)
        await ZoomService.lock_session(self.patient_id, user_id)
        await redis.set(f"session:{self.patient_id}:is_locked", "false")

        session_key = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )

        # Test
        with self.assertRaises(APIError) as err:
            await ZoomService.join_external(self.patient_id, session_key)

        self.assertEqual(str(err.exception), "Session is locked.")

        cache_lock = await redis.get(f"session:{self.patient_id}:is_locked")
        self.assertEqual(cache_lock, "true")

    async def test_join_external_deleted(self):
        """Failed to join because deleted. Even though cache wasnt proeply updatd database still denies."""
        user_id = 979
        await create_session(user_id, self.patient_id)

        redis = redis_client.get_client()
        sesson_config = await redis.hgetall(
            f"session:config:{self.patient_id}"
        )
        key = sesson_config["session_key"]

        await ZoomService.delete_session(self.patient_id, user_id)

        await redis.hset(
            f"session:config:{self.patient_id}", mapping=sesson_config
        )

        # Test
        with self.assertRaises(APIError) as err:
            await ZoomService.join_external(self.patient_id, key)

        self.assertEqual(str(err.exception), "Invalid passcode.")

    # sync participants
    async def test_sync_participants_success(self):
        user_id = 1009
        await create_session(user_id, self.patient_id)
        redis = redis_client.get_client()
        session_key = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )

        participants = [str(user_id), str("1")]

        await ZoomService.sync_participants(
            self.patient_id, session_key, participants
        )
        get = list(
            await redis.smembers(f"session:participants:{self.patient_id}")
        )

        self.assertTrue(len(get) == 2)
        await ZoomService.sync_participants(self.patient_id, session_key, [])

        isList = list(
            await redis.smembers(f"session:participants:{self.patient_id}")
        )
        self.assertFalse(isList)
        isConfig = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )
        self.assertFalse(isConfig)
        isLock = await redis.get(f"session:{self.patient_id}:is_locked")
        self.assertFalse(isLock)

        async with database.get_connection() as conn:
            result = await ZoomService._get_session(conn, self.patient_id)
            self.assertIsNone(result)

    async def test_sync_participants_with_lock(self):
        """Test sync with active session lock"""
        user_id = 1009
        await create_session(user_id, self.patient_id)
        redis = redis_client.get_client()

        # Set lock
        await redis.set(f"session:{self.patient_id}:is_locked", "1")

        session_key = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )

        # Add participants then clear
        participants = [str(user_id)]
        await ZoomService.sync_participants(
            self.patient_id, session_key, participants
        )

        await ZoomService.sync_participants(self.patient_id, session_key, [])

        # Verify everything cleared including lock
        isLock = await redis.get(f"session:{self.patient_id}:is_locked")
        self.assertFalse(isLock)

        isConfig = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )
        self.assertFalse(isConfig)

        async with database.get_connection() as conn:
            result = await ZoomService._get_session(conn, self.patient_id)
            self.assertIsNone(result)

    async def test_sync_participants_without_lock(self):
        """Test sync without session lock"""
        user_id = 1009
        await create_session(user_id, self.patient_id)
        redis = redis_client.get_client()

        session_key = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )

        participants = [str(user_id)]
        await ZoomService.sync_participants(
            self.patient_id, session_key, participants
        )

        await ZoomService.sync_participants(self.patient_id, session_key, [])

        # Verify cleared
        isConfig = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )
        self.assertFalse(isConfig)

        async with database.get_connection() as conn:
            result = await ZoomService._get_session(conn, self.patient_id)
            self.assertIsNone(result)

    async def test_sync_single_participant(self):
        """Test sync with single participant remains active"""
        user_id = 1009
        await create_session(user_id, self.patient_id)
        redis = redis_client.get_client()

        session_key = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )

        # Single participant
        await ZoomService.sync_participants(
            self.patient_id, session_key, [str(user_id)]
        )

        # Verify session still active
        participants = list(
            await redis.smembers(f"session:participants:{self.patient_id}")
        )
        self.assertEqual(len(participants), 1)

        isConfig = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )
        self.assertTrue(isConfig)

        async with database.get_connection() as conn:
            result = await ZoomService._get_session(conn, self.patient_id)
            self.assertIsNotNone(result)

    async def test_sync_invalid_key(self):
        """Test sync on invalid key"""
        user_id = 1009
        await create_session(user_id, self.patient_id)
        fake_key = "fake_session_key"

        # Try to sync non-existent session
        with self.assertRaises(APIError) as err:
            await ZoomService.sync_participants(self.patient_id, fake_key, [])

        self.assertEqual(str(err.exception), "Invalid passcode")

        # Should handle gracefully (adjust based on your implementation)
        # Either returns None or raises specific error
        redis = redis_client.get_client()
        isConfig = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )
        self.assertTrue(isConfig)

        async with database.get_connection() as conn:
            result = await ZoomService._get_session(conn, self.patient_id)
            self.assertIsNotNone(result)

    async def test_delete_already_deleted(self):
        """Test sync on invalid key"""
        user_id = 1009
        await create_session(user_id, self.patient_id)

        redis = redis_client.get_client()
        session_key = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )

        # Try to sync non-existent session
        result = await ZoomService.sync_participants(
            self.patient_id, session_key, []
        )
        self.assertEqual(result["status"], "Session deleted.")

        redis = redis_client.get_client()
        isConfig = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )
        self.assertFalse(isConfig)

        async with database.get_connection() as conn:
            result = await ZoomService._get_session(conn, self.patient_id)
            self.assertIsNone(result)

        # Try to sync non-existent session
        with self.assertRaises(APIError) as err:
            await ZoomService.sync_participants(
                self.patient_id, session_key, []
            )

        self.assertEqual(str(err.exception), "Invalid passcode")

    async def test_sync_multiple_participants_then_clear(self):
        """Test adding multiple participants then clearing all"""
        user_id = 1009
        await create_session(user_id, self.patient_id)
        redis = redis_client.get_client()

        session_key = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )

        # Add multiple participants
        participants = [str(user_id), "2", "3", "4"]
        await ZoomService.sync_participants(
            self.patient_id, session_key, participants
        )

        get = list(
            await redis.smembers(f"session:participants:{self.patient_id}")
        )
        self.assertEqual(len(get), 4)

        # Clear all
        await ZoomService.sync_participants(self.patient_id, session_key, [])

        # Verify complete cleanup
        isList = list(
            await redis.smembers(f"session:participants:{self.patient_id}")
        )
        self.assertFalse(isList)

        isConfig = await redis.hget(
            f"session:config:{self.patient_id}", "session_key"
        )
        self.assertFalse(isConfig)
