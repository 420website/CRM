# app/database.py
from typing import Optional
from contextlib import asynccontextmanager
from types_aiobotocore_s3.client import S3Client
from app.common.config import settings
import aioboto3
from botocore.config import Config


class MinioClient:
    def __init__(self) -> None:
        self.session = aioboto3.Session()
        self._client: Optional[S3Client] = None
        self._manager = None

    async def connect(self) -> None:
        # create the context manager
        self._manager = self.session.client(
            "s3",
            endpoint_url=settings.minio_url,
            aws_access_key_id=settings.minio_key_id,
            aws_secret_access_key=settings.minio_access_key,
            verify=settings.minio_verify,
            config=Config(
                signature_version=settings.minio_signature_version,
                s3={
                    "addressing_style": settings.minio_addressing_style
                },  # pyright:ignore
            ),
        )
        # actually enter the context
        self._client = await self._manager.__aenter__()  # pyright: ignore

    async def disconnect(self) -> None:
        if self._manager is not None:
            await self._manager.__aexit__(None, None, None)  # pyright: ignore
            self._manager = None
            self._client = None

    @asynccontextmanager
    async def get_client(self):
        if self._client is None:
            raise RuntimeError("S3 client not connected.")
        yield self._client


minio_client = MinioClient()
