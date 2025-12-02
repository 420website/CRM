# app/database.py
import json
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
from redis.asyncio import Redis

# client = AsyncIOMotorClient(settings.mongo_url)
client = AsyncIOMotorClient(
    settings.mongo_url,
    maxPoolSize=5,  # For 1-2GB server
    # maxPoolSize=8,    # For 4GB+ server
    minPoolSize=1,
    maxIdleTimeMS=30000,
)
mongo_db = client[settings.mongo_name]


class RedisClient:
    def __init__(self) -> None:
        self.client: Redis | None = None

    async def connect(self):
        self.client = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            decode_responses=True,
        )

    async def disconnect(self):
        if self.client:
            await self.client.aclose()

    async def ping(self):
        if not self.client:
            raise RuntimeError("Redis client not connected")

        result = await self.client.ping()  # pyright: ignore
        print(f"Ping successful: {result}")

    def get_client(self) -> Redis:
        if not self.client:
            raise RuntimeError("Redis client not connected")
        return self.client


redis_client = RedisClient()


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
        async def init_connection(conn):
            # Register JSONB codec for proper dict parsing
            await conn.set_type_codec(
                "jsonb",
                encoder=json.dumps,
                decoder=json.loads,
                schema="pg_catalog",
            )

        self.pool = await asyncpg.create_pool(
            host=settings.pg_host,
            user=settings.pg_user,
            password=settings.pg_password,
            database=settings.pg_db,
            min_size=2,  # Adjust based on server size
            max_size=5,  # Adjust based on server size
            ssl=ssl_context(),
            init=init_connection,
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
