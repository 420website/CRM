# app/database.py
import asyncio
from app.common.config import settings
from motor.motor_asyncio import AsyncIOMotorClient


class MongoClientManager:
    def __init__(self):
        self.client: AsyncIOMotorClient | None = None
        self.db = None
        self._loop = None

    async def connect(self):
        loop = asyncio.get_running_loop()

        # Recreate client if loop changed
        if self.client is None or self._loop is not loop:
            if self.client:
                self.client.close()

            self.client = AsyncIOMotorClient(
                settings.mongo_url,
                maxPoolSize=5,
                minPoolSize=1,
                maxIdleTimeMS=30000,
            )
            self.db = self.client[settings.mongo_name]
            self._loop = loop

    async def disconnect(self):
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self._loop = None

    def get_db(self):
        if self.db is None:
            raise RuntimeError("MongoDB not connected")
        return self.db


mongo_client = MongoClientManager()
