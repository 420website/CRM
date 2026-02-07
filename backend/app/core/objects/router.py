import mimetypes
from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException, Response, status
from fastapi import File, UploadFile
from app.common.storage.postgres import database
from app.core.authentication.schemas import UserRead
from app.common.dependencies import get_current_user
from app.core.objects.attachment_queries import AttachmentQueries
from app.core.objects.schemas import (
    AttachmentCreate,
    AttachmentId,
    AttachmentRead,
    PhotoCreate,
)
from app.core.objects.services import (
    AttachmentService,
    ObjectService,
    PhotoService,
)
from app.common.utils import compress_image
from app.common.logger import logger
from app.core.objects.utils import decode_jwt, generate_jwt
from app.common.config import settings

router = APIRouter(prefix="/objects", tags=["Objects"])


############
# Photos
############
@router.post("/photos/{patient_id}/{name}")
async def upload_photo(
    patient_id: int,
    name: str,
    file: UploadFile = File(...),
    _: UserRead = Depends(get_current_user),
):
    """
    Creates the object first, making the postgres insertion the point of committment,
    in the event it fails there will be an orphaned object.
    """
    bucket = "photos"
    key = f"{patient_id}/{name}"

    logger.info(
        f"Photo upload started - Patient: {patient_id}, Name: {name}, Key: {key}"
    )
    logger.info(
        f"File details - Filename: {file.filename}, ContentType: {file.content_type}, Size: {file.size if hasattr(file, 'size') else 'unknown'}"
    )

    try:
        await ObjectService.upload_object_streaming(
            bucket=bucket,
            key=key,
            file_obj=file.file,
            content_type=file.content_type or "image/jpeg",
        )

        logger.info(f"MinIO upload SUCCESS - Key: {key}")

        await PhotoService.upload_photo(
            patient_id, PhotoCreate(photo_name=name, photo_key=key)
        )
        logger.info(f"Database insert SUCCESS -  Key: {key}")
        logger.info(f"Photo Upload SUCCESS -  Key: {key}")

        return {"message": "Successfully uploaded file."}
    except Exception as e:
        logger.error(
            f"Photo upload FAILED - Patient: {patient_id}, Key: {key}, Error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.get("/photos/{patient_id}")
async def get_photo(
    patient_id: int,
    version: str = "raw",  # "base64"
    _: UserRead = Depends(get_current_user),
):
    bucket = "photos"

    try:
        key = await PhotoService.get_patient_photo_key(patient_id)

        if not key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Photo key not found for patient.",
            )

        data = await ObjectService.get_object(bucket, key)

        if version == "base64":
            file, file_type = compress_image(data)
            return {
                "file": file,
                "type": file_type,
                "name": key.split("/")[-1],
            }
        elif version == "raw":
            response = Response(
                content=data,
                media_type="application/octet-stream",
            )

            response.headers["file-name"] = key.split("/")[-1]
            return response
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid version.",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.delete("/photos/{patient_id}")
async def delete_photo(
    patient_id: int,
    _: UserRead = Depends(get_current_user),
):
    logger.info(f"Photo Delete started - Patient: {patient_id}")

    bucket = "photos"
    try:
        key = await PhotoService.delete_photo(patient_id)

        if not key:
            logger.info(
                f"Database Photo Delete Failed - Patient: {patient_id} - Key not found"
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting photo metadata.",
            )
        logger.info(f"Database Delete Success - Patient: {patient_id}")

        await ObjectService.delete_object(bucket, key)
        logger.info(f"Minio Delete Success - Patient: {patient_id}")

        return {"message": "Successfully deleted photo."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Photo Delete FAILED - Patient: {patient_id} Error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


#############
# Attachments
#############
@router.post("/attachments/{patient_id}")
async def upload_attachment(
    patient_id: int,
    file: UploadFile = File(...),
    file_name: str = Form(...),
    file_size: int = Form(...),
    mime_type: str = Form(...),
    document_type: str = Form(...),
    _: UserRead = Depends(get_current_user),
):
    """Insert into MinIO then postgres as the commit point."""
    try:
        logger.info(f"""Attachment upload started:
                        Patient: {patient_id}, 
                        Name: {file_name}, 
                        Size: {file_size}, 
                        MimeType: {mime_type}, 
                        DocType: {document_type}""")

        metadata = AttachmentCreate(
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
            document_type=document_type,
            file_key="PENDING_UPLOAD",
        )
        data = await file.read()
        key = await AttachmentService.upload_attachment(
            patient_id, data, metadata
        )

        logger.info(
            f"Attachment upload SUCCESS - Patient: {patient_id}, Key: {key}"
        )
        return {"message": "Attachment uploaded successfully."}
    except Exception as e:
        logger.error(
            f"Attachment upload FAILED - Patient: {patient_id}, Error: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.get("/attachments/{patient_id}", response_model=List[AttachmentRead])
async def list_attachment_objects(
    patient_id: int,
    _: UserRead = Depends(get_current_user),
):
    try:
        response = await AttachmentService.get_patient_attachments(patient_id)
        return response
    except Exception as e:
        logger.error(
            f"Attachment get list FAILED - Patient ID: {patient_id}, Error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.get("/attachments/{file_key:path}")
async def get_attachment(
    file_key: str,
    _: UserRead = Depends(get_current_user),
):
    try:
        data, name = await AttachmentService.get_attachment(file_key)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found for patient.",
            )
        mime_type, _encoding = mimetypes.guess_type(name)
        return Response(
            content=data,
            media_type=mime_type or "application/octet-stream",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Attachment get FAILED - Key: {file_key}, Error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.delete("/attachments/{file_key:path}")
async def delete_attachment(
    file_key: str,
    _: UserRead = Depends(get_current_user),
):
    """
    Delete from postgres then object storage, worst case orphaned object.
    """
    logger.info(f"Attachment Delete started - Key: {file_key}")

    try:
        await AttachmentService.delete_attachment(file_key)
        logger.info(f"Attachment Delet SUCCESS - key {file_key}")

        return {"message": "Successfully deleted attachment."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Attachment delete FAILED - Key: {file_key}, Error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


#############
# Share Link
#############
@router.post("/share-link")
async def create_share_link(
    body: AttachmentId,
    _: UserRead = Depends(get_current_user),
):
    # metadata = await AttachmentService.get_attachment_by_id(body.attachment_id)
    async with database.get_connection() as conn:
        metadata = await AttachmentQueries.get_attachment_by_id(
            conn, body.attachment_id
        )

    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found.",
        )

    token = generate_jwt(
        metadata.mime_type, metadata.file_key, metadata.file_name
    )
    share_url = f"{settings.app_url}/crm/share-links?token={token}"
    return {"share_url": share_url}


@router.get("/share-link/{token}/metadata")
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


@router.get("/share-link/{token}")
async def access_share_link(token: str):
    try:
        payload = decode_jwt(token)

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Url has expired.",
            )

        file_key = payload["file_key"]

        attachment = await ObjectService.get_object("attachments", file_key)
        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found.",
            )

        mime_type = payload.get("mime_type", "application/octet-stream")
        return Response(content=attachment, media_type=mime_type)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Share link access failed : Error: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )
