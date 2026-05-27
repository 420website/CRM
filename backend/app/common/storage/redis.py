# app/database.py
from app.common.config import settings
from redis.asyncio import Redis


class RedisClient:
    def __init__(self) -> None:
        self.client: Redis | None = None

    async def connect(self) -> None:
        self.client = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            decode_responses=True,
        )

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()

    async def ping(self) -> None:
        if not self.client:
            raise RuntimeError("Redis client not connected")

        result = await self.client.ping()  # pyright: ignore
        print(f"Ping successful: {result}")

    def get_client(self) -> Redis:
        if not self.client:
            raise RuntimeError("Redis client not connected")
        return self.client


redis_client = RedisClient()
