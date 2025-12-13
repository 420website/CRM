# app/auth/router.py
from datetime import datetime
from fastapi import (
    APIRouter,
    Depends,
)
from app.database import redis_client
from app.authentication.utils import SecurityService
from app.dependencies import get_current_user
from app.zoom.schema import JoinResponse

router = APIRouter(prefix="/video", tags=["References"])


async def is_session_alive(patient_id: int) -> bool:
    """Session is alive if at least one participant exists"""

    redis = redis_client.get_client()
    keys = await redis.keys(f"session:participant:{patient_id}:*")
    if not keys:
        await redis.delete(f"session:config:{patient_id}")
        return False
    return True


@router.post("/session/heartbeat/{patient_id}")
async def heartbeat(patient_id: int, user=Depends(get_current_user)):
    redis = redis_client.get_client()
    key = f"session:participant:{patient_id}:{user.id}"
    # Refresh TTL for participant
    await redis.setex(key, 90, "joined")
    return {"status": "ok"}


@router.post("/session/internal/{patient_id}")
async def internal_join_session(
    patient_id: int, user=Depends(get_current_user)
):
    redis = redis_client.get_client()
    participant_key = f"session:participant:{patient_id}:{user.id}"

    # Check if session config exists
    config = await redis.hgetall(f"session:config:{patient_id}")
    if not config:
        # No active session → create new session config
        config = {
            "sessionName": f"{patient_id}-{SecurityService.generate_secure_token(4)}",
            "sessionKey": SecurityService.generate_secure_token(4),
            "host_id": str(user.id),
            "created_at": str(datetime.now()),
            "status": "active",
        }
        await redis.hset(f"session:config:{patient_id}", mapping=config)

    # Add / refresh participant TTL
    await redis.setex(participant_key, 90, "joined")

    # Generate Zoom JWT
    token, expiry = SecurityService.generate_zoom_jwt(user.id, config)

    return JoinResponse(
        access_token=token,
        expires_at=expiry,
        sessionName=config["sessionName"],
        sessionPasscode=config["sessionKey"],
    )


@router.post("/session/leave/{patient_id}")
async def leave_session(patient_id: int, user=Depends(get_current_user)):
    redis = redis_client.get_client()
    participant_key = f"session:participant:{patient_id}:{user.id}"
    await redis.delete(participant_key)

    # Cleanup session if empty
    keys = await redis.keys(f"session:participant:{patient_id}:*")
    if not keys:
        await redis.delete(f"session:config:{patient_id}")

    return {"status": "left"}


# @router.post("/session/internal/{patient_id}")
# async def internal_join_session(
#     patient_id: int,
#     user=Depends(get_current_user),
# ):
#     if not await is_session_alive(patient_id):
#         config = {
#             "sessionName": f"{patient_id}-{settings.app_name}",
#             "sessionKey": SecurityService.generate_secure_token(4),
#             "host_id": str(user.id),
#             "created_at": str(datetime.now()),
#         }
#         (token, expiry) = SecurityService.generate_zoom_jwt(user.id, config)
#         redis = redis_client.get_client()
#         await redis.hset(f"session:config:{patient_id}", mapping=config)
#         await redis.setex(f"heartbeat:{patient_id}", 90, "alive")
#     else:
#         redis = redis_client.get_client()
#         config = await redis.hgetall(f"session:config:{patient_id}")
#
#         (token, expiry) = SecurityService.generate_zoom_jwt(user.id, config)
#
#     return JoinResponse(
#         access_token=token,
#         expires_at=expiry,
#         sessionName=config["sessionName"],
#         sessionPasscode=config["sessionKey"],
# #     )
#
#
# @router.delete("/session")
# async def delete_session(patient_id: int, user=Depends(get_current_user)):
#     redis = redis_client.get_client()
#
#     if await redis.exists(f"session:config:{patient_id}"):
#         await redis.delete(f"session:config:{patient_id}")
#
#     return {"message": "Session no longer exists."}
#
#
# @router.get("/session/external-join")
# async def external_join_session():
#     return {"message": "externally joining session."}
