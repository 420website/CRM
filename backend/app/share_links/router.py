from datetime import datetime, timedelta
import datetime as dt
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel
from app.authentication.schemas import UserRead
from app.dependencies import get_current_user
from app.registration.schemas import AttachmentRead
from app.registration.services import AttachmentService
from app.config import settings
from typing import Optional


class AttachmentId(BaseModel):
    attachment_id: int


# JWT Handling
def generate_jwt(attachment_id: int) -> str:
    expiry = datetime.now(dt.timezone.utc) + timedelta(
        minutes=settings.share_link_expire_minutes
    )

    payload = {
        "attachment_id": attachment_id,
        "exp": int(expiry.timestamp()),
        "iat": int(datetime.now(dt.timezone.utc).timestamp()),
    }

    return jwt.encode(
        payload,
        settings.jwt_access_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_jwt(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_access_secret,
            algorithms=settings.jwt_algorithm,
        )
        return payload
    except JWTError:
        return None


router = APIRouter(prefix="/share-links", tags=["Share Links"])


@router.post("/")
async def create_share_link(
    body: AttachmentId,
    user: UserRead = Depends(get_current_user),
):
    if not await AttachmentService.get_attachment_by_id(body.attachment_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found.",
        )

    token = generate_jwt(body.attachment_id)
    share_url = f"{settings.app_url}/share-links?token={token}"
    return {"share_url": share_url}


@router.get("/{token}", response_model=AttachmentRead)
async def access_share_link(token: str):
    payload = decode_jwt(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Url has expired.",
        )

    attachment = await AttachmentService.get_attachment_by_id(
        payload["attachment_id"]
    )
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found.",
        )

    return attachment
