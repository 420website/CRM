# app/auth/router.py
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from app.authentication.schemas import UserRead
from app.authentication.utils import SecurityService
from app.dependencies import get_current_user
from app.exceptions import APIError
from app.zoom.schema import GuestValidateRequest, JoinResponse
from app.zoom.services import ZoomService

router = APIRouter(prefix="/video", tags=["References"])


@router.post("/host/poll/{patient_id}")
async def refresh_host_lease(
    patient_id: int,
    user: UserRead = Depends(get_current_user),
):
    """Sync participants from Zoom - any participant can call with passcode."""
    try:

        await ZoomService.refresh_host_lease(patient_id, user.id)
        return {"message": "Host lease renewed."}
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
