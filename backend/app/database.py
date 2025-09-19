# app/database.py
import asyncpg
from asyncpg.pool import Pool
from contextlib import asynccontextmanager
from app.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
import ssl


client = AsyncIOMotorClient(settings.mongo_url)
mongo_db = client[settings.db_name]
# mongo_db.legacy_data.create_index("user_id")


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
