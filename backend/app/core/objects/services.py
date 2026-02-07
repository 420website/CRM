from typing import List, Tuple
from fastapi import HTTPException, status
from app.common.storage.postgres import database
from app.common.logger import logger
from app.core.objects.attachment_queries import AttachmentQueries
from app.core.objects.schemas import (
    AttachmentCreate,
    AttachmentRead,
    PhotoCreate,
    PhotoRead,
)
from app.core.objects.object_queries import ObjectService


class PhotoService:
    # Attachments
    @staticmethod
    async def upload_photo(patient_id: int, data: PhotoCreate) -> int | None:
        logger.info(
            f"PhotoService.upload_photo - Patient: {patient_id}, Name: {data.photo_name}, Key: {data.photo_key}"
        )

        query = """
            WITH old AS (
                SELECT patient_id, photo_key
                FROM patient_photos
                WHERE patient_id = $1
            )
            INSERT INTO patient_photos (patient_id, photo_name, photo_key)
            VALUES ($1, $2, $3)
            ON CONFLICT (patient_id) DO UPDATE
            SET photo_name  = EXCLUDED.photo_name,
                photo_key   = EXCLUDED.photo_key,
                uploaded_at = NOW()
            RETURNING id,
                   (SELECT photo_key FROM old) AS old_key;
        """
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                patient_id,
                data.photo_name,
                data.photo_key,
            )

        if row["old_key"] and row["old_key"] != data.photo_key:
            logger.info(f"Deleting old photo - Key: {row['old_key']}")
            await ObjectService.delete_object("photos", key=row["old_key"])
        else:
            logger.info("Skipping deletion - same key or no old key")

        if row:
            logger.info(
                f"Photo record saved - Patient: {patient_id}, ID: {row['id']}"
            )
        else:
            logger.error(f"Photo record not saved - Patient: {patient_id}")

        return row["id"] if row else None

    @staticmethod
    async def get_patient_photo_key(patient_id: int) -> str | None:
        query = """
        SELECT photo_key 
        FROM patient_photos 
        WHERE patient_id = $1;
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, patient_id)

        return row["photo_key"] if row else None

    @staticmethod
    async def get_photo(patient_id: int) -> PhotoRead | None:
        query = """
        SELECT * 
        FROM patient_photos 
        WHERE patient_id = $1;
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, patient_id)

        if row:
            return PhotoRead(**dict(row)) if row else None

    @staticmethod
    async def delete_photo(patient_id: int) -> str | None:
        logger.info(f"PhotoService.delete_photo - Patient: {patient_id}")

        query = """
            DELETE FROM patient_photos 
            WHERE patient_id=$1 
            RETURNING photo_key;
            """

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, patient_id)

        if row:
            logger.info(
                f"Photo record deleted - Patient: {patient_id}, Key: {row['photo_key']}"
            )
        else:
            logger.warning(f"No photo found to delete - Patient: {patient_id}")

        return row["photo_key"] if row else None


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


# --- Delete below --

# @staticmethod
# async def delete_attachment_by_id(id: int) -> None:
#     async with database.get_transaction() as conn:
#         deleted = await AttachmentQueries.delete_attachment_by_id(conn, id)
#
#         if not deleted:
#             logger.warning(f"Attachment not found - File ID: {id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Attachment not found",
#             )
#         await ObjectService.delete_object("attachments", file_key)
