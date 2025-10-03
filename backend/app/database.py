# app/database.py
from typing import Optional
import asyncpg
from asyncpg.pool import Pool
from contextlib import asynccontextmanager
from types_aiobotocore_s3.client import S3Client
from app.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
import ssl
import aioboto3
from botocore.config import Config

client = AsyncIOMotorClient(settings.mongo_url)
mongo_db = client[settings.db_name]


class MinioClient:
    def __init__(self):
        self.session = aioboto3.Session()
        self._client: Optional[S3Client] = None
        self._manager = None

    async def connect(self):
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

    async def disconnect(self):
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


def ssl_context():
    if settings.environment == "Testing":
        return None
    else:
        ssl_context = ssl.create_default_context(cafile=settings.ca_file)
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        return ssl_context


class Database:
    def __init__(self):
        self.pool: Pool

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            host=settings.host,
            user=settings.user,
            password=settings.password,
            database=settings.db,
            min_size=5,
            max_size=20,
            ssl=ssl_context(),
        )

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    @asynccontextmanager
    async def get_connection(self):
        """Get a plain connection (no transaction). Good for reads."""
        async with self.pool.acquire() as conn:
            yield conn

    @asynccontextmanager
    async def get_transaction(self):
        """Get a connection inside a transaction. Good for writes."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                yield conn


database = Database()
