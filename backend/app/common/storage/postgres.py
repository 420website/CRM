# app/database.py
import json
from typing import AsyncIterator
import asyncpg
from asyncpg.connection import Connection
from asyncpg.pool import Pool
from contextlib import asynccontextmanager
from app.common.config import settings
import ssl


def ssl_context():
    if settings.environment == "Testing":
        return None
    else:
        ssl_context = ssl.create_default_context(cafile=settings.ca_file)
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        return ssl_context


class Database:
    def __init__(self) -> None:
        self.pool: Pool

    async def connect(self) -> None:
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

    async def disconnect(self) -> None:
        if self.pool:
            await self.pool.close()

    @asynccontextmanager
    async def get_connection(self) -> AsyncIterator[Connection]:
        """Get a plain connection (no transaction). Good for reads."""
        async with self.pool.acquire() as conn:
            yield conn

    @asynccontextmanager
    async def get_transaction(self) -> AsyncIterator[Connection]:
        """Get a connection inside a transaction. Good for writes."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                yield conn


database = Database()
