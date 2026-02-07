from app.common.storage.postgres import database
from app.common.logger import logger
from app.core.objects.object_queries import ObjectService
from app.core.objects.schemas import PhotoCreate, PhotoRead


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
