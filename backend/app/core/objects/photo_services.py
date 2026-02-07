from typing import BinaryIO, Tuple
from fastapi import HTTPException, status
from app.common.storage.postgres import database
from app.common.logger import logger
from app.core.objects.photo_queries import PhotoQueries
from app.core.objects.schemas import PhotoCreate
from app.core.objects.object_queries import ObjectService


class PhotoService:
    @staticmethod
    async def upload_photo(
        patient_id: int,
        metadata: PhotoCreate,
        file: BinaryIO,
    ) -> None:
        async with database.get_transaction() as conn:
            old_key = await PhotoQueries.upload_photo(
                conn,
                patient_id,
                metadata,
            )

            await ObjectService.upload_object_streaming(
                "photos",
                metadata.photo_key,
                file,
                metadata.mime_type,
            )

        if old_key:
            logger.info(f"Old photo key to delete: {old_key}")
            await ObjectService.delete_object("photos", old_key)

    @staticmethod
    async def get_photo(patient_id: int) -> Tuple[bytes, str]:
        async with database.get_connection() as conn:
            metadata = await PhotoQueries.get_photo(conn, patient_id)

            if not metadata:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Photo key not found for patient.",
                )

        data = await ObjectService.get_object("photos", metadata.photo_key)
        return (data, metadata.photo_name)

    @staticmethod
    async def get_patient_photo_key(patient_id: int) -> str | None:
        async with database.get_connection() as conn:
            key = await PhotoQueries.get_patient_photo_key(conn, patient_id)

        return key

    @staticmethod
    async def delete_photo(patient_id: int) -> None:
        async with database.get_transaction() as conn:
            key = await PhotoQueries.delete_photo(conn, patient_id)

            if not key:
                logger.info(
                    f"Database Photo Delete Failed - Patient: {patient_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error deleting photo metadata.",
                )

        await ObjectService.delete_object("photos", key)


# -- old delete

# @staticmethod
# async def get_photo(patient_id: int) -> PhotoRead | None:
#     async with database.get_connection() as conn:
#         metadata = await PhotoQueries.get_photo
#     query = """
#     SELECT *
#     FROM patient_photos
#     WHERE patient_id = $1;
#     """
#     async with database.get_connection() as conn:
#         row = await conn.fetchrow(query, patient_id)
#
#     if row:
#         return PhotoRead(**dict(row)) if row else None
