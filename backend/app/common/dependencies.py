from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.authentication.schemas import UserRead
from app.core.authentication.services import UserService
from app.common.crypt import SecurityService

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserRead:
    token = credentials.credentials
    payload = SecurityService.decode_jwt(token)

    if payload is None or not payload.get("sub") or not payload.get("auth"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user = await UserService.get_user_by_id(
        payload.get("sub")  # pyright: ignore[reportArgumentType]
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


async def get_user_pending_mfa(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserRead:
    token = credentials.credentials
    payload = SecurityService.decode_jwt(token)

    if payload is None or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    if payload.get("auth"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This endpoint is for users who have not completed MFA",
        )

    user = await UserService.get_user_by_id(
        payload.get("sub")  # pyright: ignore[reportArgumentType]
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
