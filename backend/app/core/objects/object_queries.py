from typing import List
from app.common.storage.minio import minio_client
from app.common.logger import logger
from botocore.exceptions import ClientError


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
                print(e)
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
                logger.debug(
                    f"Starting upload object - Bucket: {bucket}, Key: {key}"
                )
                result = await client.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=data,
                )
                metadata = result.get("ResponseMetadata")
                status_code = metadata.get("HTTPStatusCode")

                if metadata.get("HTTPStatusCode") != 200:
                    logger.error(
                        f"Upload failed - Bucket: {bucket}, Key: {key}, Status: {status_code}"
                    )
                    raise Exception("Error uploading object")

                logger.info(
                    f"Upload successful - Bucket: {bucket}, Key: {key}"
                )
            except Exception as e:
                raise e

    @staticmethod
    async def upload_object_streaming(
        bucket: str,
        key: str,
        file_obj,  # File-like object from UploadFile
        content_type: str = "application/octet-stream",
        _: int = 1024 * 1024,  # 1MB chunk size
    ):
        async with minio_client.get_client() as client:
            try:
                await client.head_bucket(Bucket=bucket)
            except ClientError:
                await ObjectService.create_bucket(bucket)
            except Exception as e:
                raise e

            try:
                logger.debug(
                    f"Starting streaming put_object - Bucket: {bucket}, Key: {key}"
                )
                result = await client.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=file_obj,  # Pass file object directly
                    ContentType=content_type,
                )
                metadata = result.get("ResponseMetadata")
                status_code = metadata.get("HTTPStatusCode")

                if metadata.get("HTTPStatusCode") != 200:
                    logger.error(
                        f"Streaming upload failed - Bucket: {bucket}, Key: {key}, Status: {status_code}"
                    )
                    raise Exception("Error uploading object")

                logger.info(
                    f"Streaming upload successful - Bucket: {bucket}, Key: {key}"
                )
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
