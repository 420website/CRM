import mimetypes
from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException, Response, status
from fastapi import File, UploadFile
from app.authentication.schemas import UserRead
from app.dependencies import get_current_user
from app.objects.schemas import AttachmentCreate, AttachmentRead, PhotoCreate
from app.objects.services import AttachmentService, ObjectService, PhotoService
from app.utils import compress_image, encode_base64

router = APIRouter(prefix="/objects", tags=["Objects"])


############
# Photos
############
@router.post("/photos/{patient_id}/{name}")
async def upload_photo(
    patient_id: int,
    name: str,
    file: UploadFile = File(...),
    user: UserRead = Depends(get_current_user),
):
    """
    Creates the object first, making the postgres insertion the point of committment,
    in the event it fails there will be an orphaned object.
    """
    bucket = "photos"
    key = f"{patient_id}/{name}"

    try:
        data = await file.read()
        await ObjectService.upload_object(bucket=bucket, key=key, data=data)
        await PhotoService.upload_photo(
            patient_id, PhotoCreate(photo_name=name, photo_key=key)
        )
        return {"message": "Successfully uploaded file."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.get("/photos/{patient_id}")
async def get_photo(
    patient_id: int,
    version: str = "raw",  # "base64"
    user: UserRead = Depends(get_current_user),
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
            (file, file_type) = compress_image(data)
            return {
                "file": file,
                "type": file_type,
                "name": key.split("/")[-1],
            }
        elif version == "raw":
            return Response(
                content=data, media_type="application/octet-stream"
            )
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
    user: UserRead = Depends(get_current_user),
):
    bucket = "photos"

    try:
        key = await PhotoService.delete_photo(patient_id)

        if not key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting photo metadata.",
            )

        await ObjectService.delete_object(bucket, key)
        return {"message": "Successfully deleted photo."}
    except HTTPException:
        raise
    except Exception as e:
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
    user: UserRead = Depends(get_current_user),
):
    """Insert into MinIO then postgres as the commit point."""
    bucket = "attachments"
    key = f"{patient_id}/{file_name}"

    # Create AttachmentCreate from form fields
    metadata = AttachmentCreate(
        file_name=file_name,
        file_key=key,
        file_size=file_size,
        mime_type=mime_type,
        document_type=document_type,
    )

    try:
        data = await file.read()
        await ObjectService.upload_object(bucket=bucket, key=key, data=data)
        result = await AttachmentService.upload_attachment(
            patient_id, metadata
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error uploading attachment metadata.",
            )

        return {"message": "Attachment uploaded successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.get("/attachments/{patient_id}", response_model=List[AttachmentRead])
async def list_attachment_objects(
    patient_id: int,
    user: UserRead = Depends(get_current_user),
):
    """Postgres is the source of truth, it holds metadata."""
    response = await AttachmentService.get_patient_attachments(patient_id)
    return response


@router.get("/attachments/{patient_id}/{name}")
async def get_attachment(
    patient_id: int,
    name: str,
    version: str = "raw",  # "base64"
    user: UserRead = Depends(get_current_user),
):
    bucket = "attachments"
    key = f"{patient_id}/{name}"

    try:
        metadata = await AttachmentService.get_attachment(patient_id, name)

        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found for patient.",
            )

        data = await ObjectService.get_object(bucket, key)

        if version == "base64":
            return encode_base64(data, name)

        elif version == "raw":
            mime_type, _ = mimetypes.guess_type(name)
            return Response(
                content=data,
                media_type=mime_type or "application/octet-stream",
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid version. Must be 'raw' or 'base64'.",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.delete("/attachments/{patient_id}/{name}")
async def delete_attachment(
    patient_id: int,
    name: str,
    user: UserRead = Depends(get_current_user),
):
    """
    Delete from postgres then object storage, worst case orphaned object.
    """
    bucket = "attachments"
    key = f"{patient_id}/{name}"

    try:
        result = await AttachmentService.delete_attachment(patient_id, name)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting attachment metadata.",
            )

        await ObjectService.delete_object(bucket, key)
        return {"message": "Successfully deleted attachment."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )
