from typing import List, Tuple
from fastapi import HTTPException, status
from app.common.storage.postgres import database
from app.common.logger import logger
from app.core.objects.attachment_queries import AttachmentQueries
from app.core.objects.schemas import (
    AttachmentCreate,
    AttachmentRead,
)
from app.core.objects.object_queries import ObjectService


class AttachmentService:
    @staticmethod
    async def upload_attachment(
        patient_id: int,
        data: bytes,
        attachment: AttachmentCreate,
    ) -> str:
        async with database.get_transaction() as conn:
            attachment_id = await AttachmentQueries.create_attachment_record(
                conn, patient_id, attachment
            )
            key = f"{patient_id}/{attachment_id}/{attachment.file_name}"

            await AttachmentQueries.update_attachment_key(
                conn, attachment_id, key
            )

            await ObjectService.upload_object("attachments", key, data)

        return key

    @staticmethod
    async def get_patient_attachments(patient_id: int) -> List[AttachmentRead]:
        async with database.get_connection() as conn:
            attachments = await AttachmentQueries.get_patient_attachments(
                conn, patient_id
            )

        return attachments

    @staticmethod
    async def get_attachment(file_key: str) -> Tuple[bytes, str]:
        async with database.get_connection() as conn:
            metadata = await AttachmentQueries.get_attachment(conn, file_key)

            if not metadata:
                logger.warning(f"Attachment not found - File Key: {file_key}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Attachment not found",
                )

        data = await ObjectService.get_object("attachments", metadata.file_key)
        return (data, metadata.file_name)

    @staticmethod
    async def get_attachment_by_id(id: int) -> bytes:
        async with database.get_connection() as conn:
            metadata = await AttachmentQueries.get_attachment_by_id(conn, id)

            if not metadata:
                logger.warning(f"Attachment not found - File ID: {id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Attachment not found",
                )

        return await ObjectService.get_object("attachments", metadata.file_key)

    @staticmethod
    async def delete_attachment(file_key: str) -> None:
        async with database.get_transaction() as conn:
            deleted = await AttachmentQueries.delete_attachment(conn, file_key)

            if not deleted:
                logger.warning(f"Attachment not found - Key: {file_key}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Attachment not found",
                )
        await ObjectService.delete_object("attachments", file_key)
