# app/auth/router.py
from datetime import datetime
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from app.authentication.schemas import UserRead
from app.database import redis_client
from app.authentication.utils import SecurityService
from app.dependencies import get_current_user
from app.exceptions import APIError
from app.zoom.schema import (
    GuestValidateRequest,
    JoinResponse,
    SyncParticipantsRequest,
)
from app.zoom.services import ZoomService

router = APIRouter(prefix="/video", tags=["References"])


@router.post("/sync/{patient_id}")
async def sync_session_participants(
    patient_id: int,
    request: SyncParticipantsRequest,
):
    """Sync participants from Zoom - any participant can call with passcode."""
    try:
        result = await ZoomService.sync_participants(
            patient_id, request.session_key, request.zoom_participants
        )
        return result
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")


@router.post("/join/internal/{patient_id}")
async def internal_join_session(
    patient_id: int,
    user: UserRead = Depends(get_current_user),
):
    """Authenticated for users with a jwt."""
    try:
        config = await ZoomService.join_internal(patient_id, user.id)
        token, expiry = SecurityService.generate_zoom_jwt(str(user.id), config)

        return JoinResponse(
            access_token=token,
            expires_at=expiry,
            sessionName=config["session_name"],
            sessionPasscode=config["session_key"],
        )
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")


@router.post("/join/external/{patient_id}")
async def guest_join_session(patient_id: int, request: GuestValidateRequest):
    """Authenticated for users with a jwt."""
    try:
        config = await ZoomService.join_external(patient_id, request.passcode)
        token, expiry = SecurityService.generate_zoom_jwt(
            str(request.guest_id), config
        )

        return JoinResponse(
            access_token=token,
            expires_at=expiry,
            sessionName=config["session_name"],
            sessionPasscode=config["session_key"],
        )
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")


@router.delete("/delete/{patient_id}")
async def delete_session(
    patient_id: int,
    user: UserRead = Depends(get_current_user),
):
    """Authenticated for users with a jwt."""
    try:
        await ZoomService.delete_session(patient_id, user.id)
        return {"message": "Session no longer exists."}
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")


@router.post("/lock/{patient_id}")
async def lock_session(
    patient_id: int,
    user: UserRead = Depends(get_current_user),
):
    """Authenticated for users with a jwt."""
    try:
        await ZoomService.lock_session(patient_id, user.id)
        return {"message": "Session is now locked."}
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")


@router.post("/unlock/{patient_id}")
async def unlock_session(
    patient_id: int,
    user: UserRead = Depends(get_current_user),
):
    """Authenticated for users with a jwt."""
    try:
        await ZoomService.unlock_session(patient_id, user.id)
        return {"message": "Session is now unlocked."}
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")


### Old

#
# async def is_session_alive(patient_id: int) -> bool:
#     """Session is alive if at least one participant exists"""
#
#     redis = redis_client.get_client()
#     keys = await redis.keys(f"session:participant:{patient_id}:*")
#     if not keys:
#         await redis.delete(f"session:config:{patient_id}")
#         return False
#     return True
#
#
# @router.post("/session/heartbeat/{patient_id}")
# async def heartbeat(patient_id: int, user=Depends(get_current_user)):
#     redis = redis_client.get_client()
#     key = f"session:participant:{patient_id}:{user.id}"
#
#     # Refresh TTL for participant
#     await redis.setex(key, 90, "joined")
#     return {"status": "ok"}
#
#
# @router.post("/session/internal/{patient_id}")
# async def internal_join_session(
#     patient_id: int, user=Depends(get_current_user)
# ):
#     redis = redis_client.get_client()
#     participant_key = f"session:participant:{patient_id}:{user.id}"
#
#     # Check if session config exists
#     config = await redis.hgetall(f"session:config:{patient_id}")
#
#     if not config:
#         # No active session → create new session config
#         config = {
#             "sessionName": f"{patient_id}-{SecurityService.generate_secure_token(4)}",
#             "sessionKey": SecurityService.generate_secure_token(4),
#             "host_id": str(user.id),
#             "created_at": str(datetime.now()),
#             "status": "active",
#         }
#         await redis.hset(f"session:config:{patient_id}", mapping=config)
#
#     # Add / refresh participant TTL
#     await redis.setex(participant_key, 90, "joined")
#
#     # Generate Zoom JWT
#     token, expiry = SecurityService.generate_zoom_jwt(user.id, config)
#
#     return JoinResponse(
#         access_token=token,
#         expires_at=expiry,
#         sessionName=config["sessionName"],
#         sessionPasscode=config["sessionKey"],
#     )
#
#
# @router.post("/session/leave/{patient_id}")
# async def leave_session(patient_id: int, user=Depends(get_current_user)):
#     redis = redis_client.get_client()
#     participant_key = f"session:participant:{patient_id}:{user.id}"
#     await redis.delete(participant_key)
#
#     # Cleanup session if empty
#     keys = await redis.keys(f"session:participant:{patient_id}:*")
#     if not keys:
#         await redis.delete(f"session:config:{patient_id}")
#
#     return {"status": "left"}
#
#
# @router.post("/session/guest/heartbeat/{patient_id}/{guest_id}")
# async def guest_heartbeat(patient_id: int, guest_id: int):
#     redis = redis_client.get_client()
#     key = f"session:participant:{patient_id}:{guest_id}"
#
#     # Refresh TTL for participant
#     await redis.setex(key, 90, "joined")
#     return {"status": "ok"}
#
#
# @router.post("/session/guest/{patient_id}")
# async def guest_join_session(patient_id: int, request: GuestValidateRequest):
#     print(request)
#
#     # Check if session config exists
#     redis = redis_client.get_client()
#     config = await redis.hgetall(f"session:config:{patient_id}")
#
#     if not config:
#         raise HTTPException(status_code=400, detail="Session does not exist.")
#
#     if not config["sessionKey"] == request.passcode:
#         raise HTTPException(
#             status_code=401, detail="Invalid session or passcode."
#         )
#
#     # Add / refresh participant TTL
#     participant_key = f"session:participant:{patient_id}:{request.guest_id}"
#     await redis.setex(participant_key, 90, "joined")
#
#     # Generate Zoom JWT
#     token, expiry = SecurityService.generate_zoom_jwt(
#         str(request.guest_id), config
#     )
#
#     return JoinResponse(
#         access_token=token,
#         expires_at=expiry,
#         sessionName=config["sessionName"],
#         sessionPasscode=config["sessionKey"],
#     )
#
#
# @router.post("/session/guest/leave/{patient_id}/{guest_id}")
# async def guest_leave_session(patient_id: int, guest_id: int):
#     redis = redis_client.get_client()
#     participant_key = f"session:participant:{patient_id}:{guest_id}"
#     await redis.delete(participant_key)
#
#     # Cleanup session if empty
#     keys = await redis.keys(f"session:participant:{patient_id}:*")
#     if not keys:
#         await redis.delete(f"session:config:{patient_id}")
#
#     return {"status": "left"}
#
#
# # @router.delete("/session")
# # async def delete_session(patient_id: int, user=Depends(get_current_user)):
# #     redis = redis_client.get_client()
# #
# #     if await redis.exists(f"session:config:{patient_id}"):
# #         await redis.delete(f"session:config:{patient_id}")
# #
# #     return {"message": "Session no longer exists."}
