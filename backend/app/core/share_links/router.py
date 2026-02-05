from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from app.core.authentication.schemas import UserRead
from app.common.dependencies import get_current_user
from app.common.config import settings
from app.core.objects.services import AttachmentService, ObjectService
from app.core.share_links.utils import decode_jwt, generate_jwt

router = APIRouter(prefix="/share-links", tags=["Share Links"])


class AttachmentId(BaseModel):
    attachment_id: int


@router.post("/")
async def create_share_link(
    body: AttachmentId,
    _: UserRead = Depends(get_current_user),
):
    metadata = await AttachmentService.get_attachment_by_id(body.attachment_id)

    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found.",
        )

    token = generate_jwt(
        metadata.mime_type, metadata.patient_id, metadata.file_name
    )
    share_url = f"{settings.app_url}/crm/share-links?token={token}"
    return {"share_url": share_url}


@router.get("/{token}/metadata")
async def get_share_link_metadata(token: str):
    payload = decode_jwt(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Url has expired.",
        )
    return {
        "file_name": payload["file_name"],
        "mime_type": payload["mime_type"],
    }


@router.get("/{token}")
async def access_share_link(token: str):
    payload = decode_jwt(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Url has expired.",
        )
    name = payload["file_name"]
    key = f"{payload['patient_id']}/{name}"

    attachment = await ObjectService.get_object("attachments", key)

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found.",
        )

    return Response(content=attachment)
