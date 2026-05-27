from typing import Union
from asyncpg import Connection
from app.common.logger import logger
from app.core.objects.schemas import PhotoCreate, PhotoRead


class PhotoQueries:
    @staticmethod
    async def upload_photo(
        conn: Connection,
        patient_id: int,
        data: PhotoCreate,
    ) -> Union[str, None]:
        """Upsert the photo metadata."""

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
               CASE 
                   WHEN (SELECT photo_key FROM old) IS NOT NULL 
                    AND (SELECT photo_key FROM old) != $3
                   THEN (SELECT photo_key FROM old)
                   ELSE NULL
               END AS old_key;
        """
        row = await conn.fetchrow(
            query,
            patient_id,
            data.photo_name,
            data.photo_key,
        )

        if not row:
            logger.error(f"Photo record not saved - Patient: {patient_id}")
            raise Exception("Failed to save photo metadata")

        logger.info(f"Photo metadata saved - Patient: {patient_id}")
        return row["old_key"]

    @staticmethod
    async def get_photo(
        conn: Connection,
        patient_id: int,
    ) -> Union[PhotoRead, None]:
        query = """
        SELECT * 
        FROM patient_photos 
        WHERE patient_id = $1;
        """
        row = await conn.fetchrow(query, patient_id)
        return PhotoRead(**dict(row)) if row else None

    @staticmethod
    async def get_patient_photo_key(
        conn: Connection,
        patient_id: int,
    ) -> Union[str, None]:
        query = """
        SELECT photo_key
        FROM patient_photos
        WHERE patient_id = $1;
        """
        row = await conn.fetchrow(query, patient_id)
        return row["photo_key"] if row else None

    @staticmethod
    async def delete_photo(
        conn: Connection,
        patient_id: int,
    ) -> Union[str, None]:
        query = """
        DELETE FROM patient_photos 
        WHERE patient_id=$1
        RETURNING photo_key;
        """
        row = await conn.fetchrow(query, patient_id)
        return row["photo_key"] if row else None


# -- Delete ---


# @staticmethod
# async def get_patient_photo_key(
#     conn: Connection,
#     patient_id: int,
# ) -> Union[str, None]:
#     query = """
#     SELECT photo_key
#     FROM patient_photos
#     WHERE patient_id = $1;
#     """
#     row = await conn.fetchrow(query, patient_id)
#     return row["photo_key"] if row else Non
#
#
# async def upload_photo(
#     conn: Connection, patient_id: int, data: PhotoCreate
# ) -> Union[int, None]:
#     """Upsert the photo metadata."""
#     query = """
#         WITH old AS (
#             SELECT patient_id, photo_key
#             FROM patient_photos
#             WHERE patient_id = $1
#         )
#         INSERT INTO patient_photos (patient_id, photo_name, photo_key)
#         VALUES ($1, $2, $3)
#         ON CONFLICT (patient_id) DO UPDATE
#         SET photo_name  = EXCLUDED.photo_name,
#             photo_key   = EXCLUDED.photo_key,
#             uploaded_at = NOW()
#         RETURNING id,
#                (SELECT photo_key FROM old) AS old_key;
#     """
#     async with database.get_transaction() as conn:
#         row = await conn.fetchrow(
#             query,
#             patient_id,
#             data.photo_name,
#             data.photo_key,
#         )
#
#     if row["old_key"] and row["old_key"] != data.photo_key:
#         logger.info(f"Deleting old photo - Key: {row['old_key']}")
#         await ObjectService.delete_object("photos", key=row["old_key"])
#     else:
#         logger.info("Skipping deletion - same key or no old key")
#
#     if row:
#         logger.info(
#             f"Photo record saved - Patient: {patient_id}, ID: {row['id']}"
#         )
#     else:
#         logger.error(f"Photo record not saved - Patient: {patient_id}")
#
#     return row["id"] if row else None


# return int(result.split()[1]) > 0
#
# if row:
#     logger.info(
#         f"Photo record deleted - Patient: {patient_id}, Key: {row['photo_key']}"
#     )
# else:
#     logger.warning(f"No photo found to delete - Patient: {patient_id}")
#
# return row["photo_key"] if row else None
