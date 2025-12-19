from typing import List
from asyncpg.connection import Connection
from app.authentication.utils import SecurityService
from app.logger import logger
from app.database import database
from app.exceptions import (
    APIError,
    ForbiddenError,
    NotFoundError,
    SessionLockedError,
    UnauthorizedError,
)
from app.zoom.schema import SessionConfig
from app.database import redis_client


class ZoomService:
    @staticmethod
    async def _get_session(conn: Connection, patient_id: int) -> dict | None:
        """Internal: Get session from DB using provided connection."""
        query = "SELECT * FROM zoom_session WHERE patient_id=$1 AND deleted_at IS NULL"
        row = await conn.fetchrow(query, patient_id)
        return dict(row) if row else None

    @staticmethod
    async def _soft_delete_session(conn: Connection, patient_id: int):
        """Internal: Soft delete session."""
        query = """
            UPDATE zoom_session
            SET is_deleted = TRUE, deleted_at = NOW()
            WHERE patient_id = $1
            RETURNING is_deleted
        """
        result = await conn.fetchval(query, patient_id)
        return result is not None

    @staticmethod
    async def _valid_passcode(
        conn: Connection, patient_id: int, session_key: str
    ) -> bool:
        query = """
        SELECT EXISTS (
            SELECT 1 
            FROM zoom_session 
            WHERE patient_id=$1 
            AND session_key=$2
            AND deleted_at IS NULL
        );
        """
        result = await conn.fetchval(query, patient_id, session_key)
        return result

    @staticmethod
    async def _check_session_exists(conn: Connection, patient_id: int) -> bool:
        """Internal: Check if session exists and is not deleted."""
        query = """
            SELECT patient_id 
            FROM zoom_session 
            WHERE patient_id=$1 AND deleted_at IS NULL
        """
        result = await conn.fetchval(query, patient_id)
        return result is not None

    @staticmethod
    async def _check_is_host(
        conn: Connection, patient_id: int, user_id: int
    ) -> bool:
        """Internal: Check if user is the host of the session."""
        query = """
            SELECT host_id 
            FROM zoom_session 
            WHERE patient_id=$1 AND deleted_at IS NULL
        """
        host_id = await conn.fetchval(query, patient_id)
        return host_id == user_id if host_id is not None else False

    @staticmethod
    async def _check_lock(conn: Connection, patient_id: int) -> bool:
        """Internal: Check lock status from DB using provided connection."""
        query = """
            SELECT is_locked 
            FROM zoom_session 
            WHERE patient_id=$1 AND deleted_at IS NULL
        """
        return await conn.fetchval(query, patient_id) or False

    @staticmethod
    async def _lock_session(
        conn: Connection, patient_id: int, user_id: int
    ) -> bool:
        """Internal: Lock session in DB using provided connection."""
        query = """
            UPDATE zoom_session
            SET is_locked=TRUE, locked_at=NOW()
            WHERE patient_id=$1 AND host_id=$2 AND deleted_at IS NULL
            RETURNING is_locked
        """
        result = await conn.fetchval(query, patient_id, user_id)
        return result is not None

    @staticmethod
    async def _unlock_session(
        conn: Connection,
        patient_id: int,
        user_id: int,
    ) -> bool:
        """Internal: Unlock session in DB using provided connection."""
        query = """
            UPDATE zoom_session
            SET is_locked=FALSE, locked_at=NULL
            WHERE patient_id=$1 AND host_id=$2 AND deleted_at IS NULL
            RETURNING is_locked
        """
        result = await conn.fetchval(query, patient_id, user_id)
        return result is not None and not result  # result false

    @staticmethod
    async def _upsert_session(
        conn: Connection, config: SessionConfig
    ) -> dict | None:
        """Internal: Update or insert session config in DB with provided connection"""
        query = """
        INSERT INTO zoom_session(patient_id, session_name, session_key, host_id, is_locked, locked_at, is_deleted, deleted_at, created_at) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (patient_id) 
        DO UPDATE SET 
            session_name=EXCLUDED.session_name, 
            session_key=EXCLUDED.session_key,
            host_id=EXCLUDED.host_id,
            is_locked=EXCLUDED.is_locked, 
            locked_at=EXCLUDED.locked_at, 
            is_deleted=EXCLUDED.is_deleted, 
            deleted_at=EXCLUDED.deleted_at,
            created_at=EXCLUDED.created_at
        RETURNING *
        """
        row = await conn.fetchrow(
            query,
            config.patient_id,
            config.session_name,
            config.session_key,
            config.host_id,
            config.is_locked,
            config.locked_at,
            config.is_deleted,
            config.deleted_at,
            config.created_at,
        )
        return dict(row) if row else None

    @staticmethod
    async def delete_session(patient_id: int, user_id: int):
        """Soft deletes the session by toggling flag."""
        async with database.get_transaction() as conn:
            if not await ZoomService._check_session_exists(conn, patient_id):
                raise NotFoundError("Session not found")

            if not await ZoomService._check_is_host(conn, patient_id, user_id):
                raise ForbiddenError("User is not the session host")

            await ZoomService._soft_delete_session(conn, patient_id)

        # DB committed, now clean cache
        try:
            redis = redis_client.get_client()
            await redis.delete(f"session:config:{patient_id}")
            await redis.delete(f"session:{patient_id}:is_locked")
        except Exception as e:
            logger.warning(
                f"Failed to clear Redis cache for session {patient_id}: {e}"
            )

    @staticmethod
    async def lock_session(patient_id: int, user_id: int):
        """Lock the session disabling particapant joins."""
        async with database.get_transaction() as conn:
            if not await ZoomService._check_session_exists(conn, patient_id):
                raise NotFoundError("Session not found")

            if not await ZoomService._check_is_host(conn, patient_id, user_id):
                raise ForbiddenError("User is not the session host")

            is_locked = await ZoomService._lock_session(
                conn, patient_id, user_id
            )

            if not is_locked:
                raise APIError("Failed to lock session.")

        try:
            redis = redis_client.get_client()
            await redis.set(f"session:{patient_id}:is_locked", "true")
        except Exception as e:
            logger.warning(
                f"Failed to update Redis cache for session {patient_id}: {e}"
            )

    @staticmethod
    async def unlock_session(patient_id: int, user_id: int):
        """Unlock the session disabling particapant joins."""
        async with database.get_transaction() as conn:
            if not await ZoomService._check_session_exists(conn, patient_id):
                raise NotFoundError("Session not found")

            if not await ZoomService._check_is_host(conn, patient_id, user_id):
                raise ForbiddenError("User is not the session host")

            is_unlocked = await ZoomService._unlock_session(
                conn, patient_id, user_id
            )

            if not is_unlocked:
                raise APIError("Failed to unlock session.")

        try:
            redis = redis_client.get_client()
            await redis.set(f"session:{patient_id}:is_locked", "false")
        except Exception as e:
            logger.warning(
                f"Failed to update Redis cache for session {patient_id}: {e}"
            )

    @staticmethod
    async def join_internal(patient_id: int, user_id: int) -> dict:
        """Internal user joins - can create session and become host."""
        redis = redis_client.get_client()

        # Quick cache check for lock
        cached_lock = await redis.get(f"session:{patient_id}:is_locked")
        if cached_lock == "true":
            raise SessionLockedError("Session is locked.")

        async with database.get_transaction() as conn:
            # Double-check lock in DB
            if await ZoomService._check_lock(conn, patient_id):
                await redis.set(f"session:{patient_id}:is_locked", "true")
                raise SessionLockedError("Session is locked.")

            # Get or create session
            session_dict = await ZoomService._get_session(conn, patient_id)

            if session_dict:
                return session_dict

            # Create new session with user as host
            config = SessionConfig(
                patient_id=patient_id,
                session_name=f"{patient_id}-{SecurityService.generate_secure_token(4)}",
                session_key=SecurityService.generate_secure_token(6),
                host_id=user_id,
                is_locked=False,
                locked_at=None,
                is_deleted=False,
                deleted_at=None,
                created_at=None,
            )
            session_dict = await ZoomService._upsert_session(conn, config)

        # Cache result
        try:
            await redis.hset(
                f"session:config:{patient_id}", mapping=config.encode()
            )
        except Exception as e:
            logger.warning(f"Failed to cache session {patient_id}: {e}")

        return session_dict

    @staticmethod
    async def join_external(patient_id: int, session_key: str):
        """External user joins - must have valid passcode, cannot be host."""
        redis = redis_client.get_client()

        # Check cache for passcode
        passcode = await redis.hget(
            f"session:config:{patient_id}", "session_key"
        )
        if passcode != session_key:
            raise ForbiddenError("Invalid passcode.")

        # Quick cache check for lock
        cached_lock = await redis.get(f"session:{patient_id}:is_locked")
        if cached_lock == "true":
            raise SessionLockedError("Session is locked.")

        async with database.get_transaction() as conn:
            if not await ZoomService._valid_passcode(
                conn, patient_id, session_key
            ):
                raise ForbiddenError("Invalid passcode.")

            # Double-check lock in DB
            if await ZoomService._check_lock(conn, patient_id):
                await redis.set(f"session:{patient_id}:is_locked", "true")
                raise SessionLockedError("Session is locked.")

            # Get session (must exist for external users)
            session_dict = await ZoomService._get_session(conn, patient_id)

            if not session_dict:
                raise APIError("Session not found.")

            return session_dict

    @staticmethod
    async def sync_participants(
        patient_id: int,
        session_key: str,
        zoom_participants: List[str],
    ):
        """Sync participant list - idempotent, safe to call multiple times."""
        async with database.get_transaction() as conn:
            # Validate passcode
            if not await ZoomService._valid_passcode(
                conn, patient_id, session_key
            ):
                raise ForbiddenError("Invalid passcode")

            redis = redis_client.get_client()

            # Handle empty session
            if len(zoom_participants) == 0:
                await ZoomService._soft_delete_session(conn, patient_id)
                await redis.delete(f"session:config:{patient_id}")
                await redis.delete(f"session:{patient_id}:is_locked")
                await redis.delete(f"session:participants:{patient_id}")
                return {"status": "Session deleted."}

            # Replace participant list (idempotent)
            await redis.delete(f"session:participants:{patient_id}")
            for uid in zoom_participants:
                await redis.sadd(f"session:participants:{patient_id}", uid)

        return {"status": "synced", "count": len(zoom_participants)}
