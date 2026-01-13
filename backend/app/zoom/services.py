from app.authentication.utils import SecurityService
from datetime import datetime, timezone
from app.exceptions import (
    ForbiddenError,
    NotFoundError,
    SessionExpiredError,
    SessionLockedError,
)
from app.zoom.schema import SessionConfig
from app.database import redis_client
import jwt
import time
import httpx
from app.config import settings


class ZoomVideoSDKService:
    BASE_URL = "https://api.zoom.us/v2/videosdk"

    @staticmethod
    def _generate_api_jwt() -> str:
        """Generate JWT for API authentication (server-to-server)."""
        payload = {
            "iss": settings.api_key,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,  # 1 hour
        }
        return jwt.encode(
            payload, settings.api_secret, algorithm=settings.jwt_algorithm
        )

    @staticmethod
    def _generate_client_jwt(
        user_id: str,
        session_name: str,
        role: int = 0,
    ) -> str:
        payload = {
            "app_key": settings.sdk_key,
            "role_type": role,
            "tpc": session_name,
            "version": 1,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,  # 1 hour
            "video_webrtc_mode": 1,
            "user_identity": user_id,
            # "telemetry_tracking_id": "telemetryTrackingId",
        }

        return jwt.encode(
            payload,
            settings.sdk_secret,
            algorithm=settings.jwt_algorithm,
        )

    @staticmethod
    async def _request(method: str, endpoint: str, **kwargs):
        token = ZoomVideoSDKService._generate_api_jwt()

        async with httpx.AsyncClient() as client:
            return await client.request(
                method,
                f"{ZoomVideoSDKService.BASE_URL}{endpoint}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                timeout=10.0,
                **kwargs,
            )

    @staticmethod
    async def get_zoom_session_id(session_name: str) -> str | None:
        sessions = await ZoomVideoSDKService.list_sessions()
        for s in sessions:
            if s["session_name"].lower() == session_name.lower():
                return s["id"]
        return None

    @staticmethod
    async def get_session(session_name: str) -> dict | None:
        """Get Zoom session by session_name."""
        session_id = await ZoomVideoSDKService.get_zoom_session_id(
            session_name
        )
        if not session_id:
            return None

        response = await ZoomVideoSDKService._request(
            "GET", f"/sessions/{session_id}"
        )
        return response.json() if response.status_code == 200 else None

    @staticmethod
    async def get_session_users(session_name: str) -> list:
        """Get participants by session_name."""
        session_id = await ZoomVideoSDKService.get_zoom_session_id(
            session_name
        )
        if not session_id:
            return []

        response = await ZoomVideoSDKService._request(
            "GET", f"/sessions/{session_id}/users"
        )
        return (
            response.json().get("participants", [])
            if response.status_code == 200
            else []
        )

    @staticmethod
    async def list_sessions(page_size: int = 30) -> list:
        """List all active sessions (Zoom REST)."""
        response = await ZoomVideoSDKService._request(
            "GET", "/sessions", params={"page_size": page_size}
        )
        if response.status_code == 200:
            return response.json().get("sessions", [])
        return []


class ZoomService:
    @staticmethod
    async def _create_zoom_session(
        patient_id: int, user_id: int
    ) -> SessionConfig:

        now = datetime.now(timezone.utc).isoformat()

        config = SessionConfig(
            session_name=f"{patient_id}-{settings.app_name}-{SecurityService.generate_secure_token(4)}",
            session_key=SecurityService.generate_secure_token(6),
            host_id=user_id,
            is_locked=False,  # host owns session
            host_last_seen_at=now,  # host presences controls session
        )

        redis = redis_client.get_client()
        await redis.hset(
            f"session:metadata:{patient_id}", mapping=config.encode()
        )

        return config

    @staticmethod
    async def _get_session_metadata(patient_id: int) -> SessionConfig | None:
        """Fetch session metadata from Redis and decode types."""
        redis = redis_client.get_client()
        data = await redis.hgetall(f"session:metadata:{patient_id}")
        if not data:
            return None

        # Convert Redis hash (all strings) to typed SessionConfig
        return SessionConfig.decode(data)

    @staticmethod
    async def _delete_session_cache(patient_id: int):
        # Cleanup Redis
        redis = redis_client.get_client()
        await redis.delete(f"session:metadata:{patient_id}")

    @staticmethod
    async def _refresh_host_lease(patient_id: int):
        redis = redis_client.get_client()

        await redis.hset(
            f"session:metadata:{patient_id}",
            "host_last_seen_at",
            datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    async def _is_session_alive(patient_id: int) -> bool:
        metadata = await ZoomService._get_session_metadata(patient_id)

        if not metadata:
            return False  # no record → explicitly ended

        # last_seen_raw = metadata.get("host_last_seen_at")
        if not metadata.host_last_seen_at:
            return False

        last_seen = datetime.fromisoformat(metadata.host_last_seen_at)
        now = datetime.now(timezone.utc)

        return (now - last_seen).total_seconds() <= settings.host_grace_seconds

    @staticmethod
    async def _check_is_host(patient_id: int, user_id: int) -> bool:
        """Internal: Check if user is the host of the session."""
        metadata = await ZoomService._get_session_metadata(patient_id)

        if not metadata:
            raise NotFoundError("Session not found")

        return metadata.host_id != user_id

    @staticmethod
    async def _check_lock(patient_id: int) -> bool:
        """Check if session is locked."""
        redis = redis_client.get_client()
        locked = await redis.hget(
            f"session:metadata:{patient_id}", "is_locked"
        )
        return locked == "true" if locked else False

    @staticmethod
    async def _valid_passcode(patient_id: int, session_key: str) -> bool:
        redis = redis_client.get_client()
        key = await redis.hget(f"session:metadata:{patient_id}", "session_key")

        return key == session_key

    @staticmethod
    async def lock_session(patient_id: int, user_id: int):
        """Lock session - prevents new participants from joining."""
        metadata = await ZoomService._get_session_metadata(patient_id)

        if not metadata:
            raise NotFoundError("Session not found")

        if metadata.host_id != user_id:
            raise ForbiddenError("User is not the session host")

        # Set lock flag in Redis
        redis = redis_client.get_client()
        await redis.hset(f"session:metadata:{patient_id}", "is_locked", "true")

    @staticmethod
    async def unlock_session(patient_id: int, user_id: int):
        """Unlock session - allows participants to join."""
        metadata = await ZoomService._get_session_metadata(patient_id)

        if not metadata:
            raise NotFoundError("Session not found")

        if metadata.host_id != user_id:
            raise ForbiddenError("User is not the session host")

        # Remove lock flag
        redis = redis_client.get_client()
        await redis.hset(
            f"session:metadata:{patient_id}", "is_locked", "false"
        )

    @staticmethod
    async def join_internal(patient_id: int, user_id: int) -> dict:
        """Internal user joins - can create session and become host."""

        session_config = await ZoomService._get_session_metadata(patient_id)

        # If session exists after verification
        if session_config:
            alive = await ZoomService._is_session_alive(patient_id)

            if not alive:
                await ZoomService._delete_session_cache(patient_id)
                config = await ZoomService._create_zoom_session(
                    patient_id, user_id
                )
                return config.model_dump()

            is_locked = await ZoomService._check_lock(patient_id)
            host_id = session_config.host_id

            # Host rejoining → refresh lease
            if is_locked and host_id != user_id:
                raise SessionLockedError("Session is locked.")

            if host_id == user_id:
                await ZoomService._refresh_host_lease(patient_id)

            return session_config.model_dump()

        # Session doesn't exist → create new
        config = await ZoomService._create_zoom_session(patient_id, user_id)
        return config.model_dump()

    @staticmethod
    async def join_external(
        patient_id: int,
        session_key: str,
    ) -> dict:
        """External user joins - must have valid passcode, cannot be host."""

        # Get session metadata from our cache/db
        local_session = await ZoomService._get_session_metadata(patient_id)

        if not local_session:
            raise NotFoundError("Session is not active")

        # Verify Zoom session exists
        if not await ZoomService._is_session_alive(patient_id):
            raise NotFoundError("Session is not active")

        # Validate passcode
        if local_session.session_key != session_key:
            raise ForbiddenError("Invalid passcode.")

        # Check lock
        is_locked = await ZoomService._check_lock(patient_id)
        if is_locked:
            raise SessionLockedError("Session is locked.")

        return local_session.model_dump()

    @staticmethod
    async def delete_session(patient_id: int, user_id: int):
        """Delete session from Zoom and cleanup Redis."""
        metadata = await ZoomService._get_session_metadata(patient_id)

        if not metadata:
            raise NotFoundError("Session not found")

        if metadata.host_id != user_id:
            raise ForbiddenError("User is not the session host")

        # Cleanup Redis
        redis = redis_client.get_client()
        await redis.delete(f"session:metadata:{patient_id}")

    @staticmethod
    async def refresh_host_lease(patient_id: int, user_id: int):
        metadata = await ZoomService._get_session_metadata(patient_id)

        if not metadata:
            raise NotFoundError("Session not found")

        if metadata.host_id != user_id:
            raise ForbiddenError("User is not the session host")

        alive = await ZoomService._is_session_alive(patient_id)
        if not alive:
            raise SessionExpiredError("Host session has expired")

        await ZoomService._refresh_host_lease(patient_id)
