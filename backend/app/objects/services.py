from typing import List, Union
from app.database import database, minio_client
from botocore.exceptions import ClientError
from app.objects.schemas import (
    AttachmentCreate,
    AttachmentRead,
    PhotoCreate,
    PhotoRead,
)


class ObjectService:
    @staticmethod
    async def create_bucket(bucket: str):
        async with minio_client.get_client() as client:
            try:
                response = await client.create_bucket(Bucket=bucket)
                metadata = response.get("ResponseMetadata")

                if metadata.get("HTTPStatusCode") != 200:
                    raise Exception(f"Error creating bucket: {bucket}")
            except Exception as e:
                raise e

    @staticmethod
    async def delete_bucket(bucket: str):
        async with minio_client.get_client() as client:
            try:
                response = await client.delete_bucket(Bucket=bucket)
                metadata = response.get("ResponseMetadata")

                if metadata.get("HTTPStatusCode") != 204:
                    raise Exception(f"Error deleting bucket: {bucket}")
            except ClientError as e:
                if e.response.get("Error", {}).get("Code") == "NoSuchBucket":
                    return
                raise e
            except Exception as e:
                raise e

    @staticmethod
    async def list_buckets() -> List[str]:
        async with minio_client.get_client() as client:
            try:
                resp = await client.list_buckets()
                metadata = resp.get("ResponseMetadata")

                if metadata.get("HTTPStatusCode") != 200:
                    raise Exception("Error uploading object")

                buckets = [
                    name
                    for b in resp["Buckets"]
                    if (name := b.get("Name")) is not None
                ]
                return buckets
            except Exception as e:
                raise e

    @staticmethod
    async def upload_object(bucket: str, key: str, data: bytes):
        async with minio_client.get_client() as client:
            try:
                await client.head_bucket(Bucket=bucket)
            except ClientError:
                await ObjectService.create_bucket(bucket)
            except Exception as e:
                raise e

            try:
                result = await client.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=data,
                )
                metadata = result.get("ResponseMetadata")

                if metadata.get("HTTPStatusCode") != 200:
                    raise Exception("Error uploading object")
            except Exception as e:
                raise e

    @staticmethod
    async def upload_object_streaming(
        bucket: str,
        key: str,
        file_obj,  # File-like object from UploadFile
        content_type: str = "application/octet-stream",
        chunk_size: int = 1024 * 1024,  # 1MB chunks
    ):
        async with minio_client.get_client() as client:
            try:
                await client.head_bucket(Bucket=bucket)
            except ClientError:
                await ObjectService.create_bucket(bucket)
            except Exception as e:
                raise e

            try:
                result = await client.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=file_obj,  # Pass file object directly
                    ContentType=content_type,
                )
                metadata = result.get("ResponseMetadata")

                if metadata.get("HTTPStatusCode") != 200:
                    raise Exception("Error uploading object")
            except Exception as e:
                raise e

    @staticmethod
    async def get_object(bucket: str, key: str) -> bytes:
        async with minio_client.get_client() as client:
            if not await client.head_bucket(Bucket=bucket):
                raise Exception("Bucket doesn't exist.")
            try:
                response = await client.get_object(Bucket=bucket, Key=key)
                metadata = response.get("ResponseMetadata")

                if metadata.get("HTTPStatusCode") != 200:
                    raise Exception("Error getting object")

                return await response["Body"].read()
            except Exception as e:
                raise e

    @staticmethod
    async def delete_object(bucket: str, key: str):
        async with minio_client.get_client() as client:
            try:
                response = await client.delete_object(Bucket=bucket, Key=key)
                metadata = response.get("ResponseMetadata")

                if metadata.get("HTTPStatusCode") != 204:
                    raise Exception(f"Error deleting object : {key}")
            except ClientError as e:
                if e.response.get("Error", {}).get("Code") == "NoSuchBucket":
                    return
                raise e
            except Exception as e:
                raise e

    @staticmethod
    async def list_objects(bucket: str, prefix: str = ""):
        async with minio_client.get_client() as client:
            try:
                response = await client.list_objects_v2(
                    Bucket=bucket,
                    Prefix=prefix,
                )
                metadata = response.get("ResponseMetadata")

                if metadata.get("HTTPStatusCode") != 200:
                    raise Exception("Error uploading object")

                return [obj.get("Key") for obj in response.get("Contents", [])]
            except Exception as e:
                raise e

    @staticmethod
    async def delete_objects(bucket: str, prefix: str):
        try:
            keys = await ObjectService.list_objects(bucket, prefix)

            if keys and len(keys) > 0:
                for k in keys:
                    if k:
                        await ObjectService.delete_object(bucket, k)
        except Exception as e:
            raise e


class PhotoService:
    # Attachments
    @staticmethod
    async def upload_photo(patient_id: int, data: PhotoCreate) -> int | None:
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

        if row["old_key"]:
            await ObjectService.delete_object("photos", key=row["old_key"])

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
        query = """
            DELETE FROM patient_photos 
            WHERE patient_id=$1 
            RETURNING photo_key;
            """

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, patient_id)

        return row["photo_key"] if row else None


class AttachmentService:
    # Attachments
    @staticmethod
    async def upload_attachment(
        patient_id: int,
        attachment: AttachmentCreate,
    ) -> int | None:
        """
        Could also jsut have not duplciate so users have to remove old one
        before creating with same name.
        """

        query = """
        INSERT INTO attachments (
            patient_id, file_name, file_key, file_size,
            mime_type, document_type
        )
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (patient_id, file_name)
        DO UPDATE SET 
            file_name = EXCLUDED.file_name,
            file_key = EXCLUDED.file_key,
            file_size = EXCLUDED.file_size, 
            mime_type = EXCLUDED.mime_type,
            document_type = EXCLUDED.document_type
        RETURNING id;
        """
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                patient_id,
                attachment.file_name,
                attachment.file_key,
                attachment.file_size,
                attachment.mime_type,
                attachment.document_type,
            )
        if row and "id" in row:
            return row["id"]
        return None

    @staticmethod
    async def get_patient_attachments(patient_id: int) -> List[AttachmentRead]:
        query = """
        SELECT * 
        FROM attachments 
        WHERE patient_id = $1 
        ORDER BY uploaded_at DESC;
        """
        async with database.get_connection() as conn:
            rows = await conn.fetch(query, patient_id)

        result = []
        if rows:
            for row in rows:
                result.append(AttachmentRead(**dict(row)))
        return result

    @staticmethod
    async def get_attachment(
        patient_id: int, name: str
    ) -> Union[AttachmentRead, None]:
        query = """
        SELECT * 
        FROM attachments  
        WHERE patient_id = $1 
            AND file_name = $2;
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, patient_id, name)

        if row:
            return AttachmentRead(**dict(row)) if row else None

    @staticmethod
    async def get_attachment_by_id(id: int) -> Union[AttachmentRead, None]:
        query = """
        SELECT * 
        FROM attachments  
        WHERE id = $1; 
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, id)

        if row:
            return AttachmentRead(**dict(row)) if row else None

    @staticmethod
    async def delete_attachment(patient_id: int, name: str) -> bool:
        query = """
            DELETE FROM attachments 
            WHERE patient_id=$1 
                AND file_name=$2
            RETURNING id;
        """

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, patient_id, name)
            return bool(row)

    @staticmethod
    async def delete_attachment_by_id(id: int) -> bool:
        query = """DELETE FROM attachments WHERE id=$1 RETURNING id;"""

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, id)
            return bool(row)
