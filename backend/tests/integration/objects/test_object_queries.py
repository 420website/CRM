# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportAttributeAccessIssue=none
import asyncio
from unittest import IsolatedAsyncioTestCase
from app.common.storage.minio import minio_client
from app.core.objects.object_queries import ObjectService


def read_file(path: str) -> bytes:
    with open(path, "rb") as file:
        file_bytes = file.read()
        return file_bytes


class TestObjectServices(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await minio_client.connect()

        self.bucket = "testing"
        self.key = "test_file"
        self.object_path = "tests/integration/objects/docs/test-pdf.pdf"

        await ObjectService.create_bucket(self.bucket)

    async def asyncTearDown(self) -> None:
        await ObjectService.delete_object(self.bucket, "test_file")
        await ObjectService.delete_bucket("testing")
        await minio_client.disconnect()

    async def test_create_and_list_buckets_success(self):
        bucket = "other"
        await ObjectService.create_bucket(bucket)

        # Test
        check = await ObjectService.list_buckets()
        self.assertIn(bucket, check)

        await ObjectService.delete_bucket(bucket)

    async def test_list_objects(self):
        data = read_file(self.object_path)
        key = "test_object"
        await ObjectService.upload_object(self.bucket, key, data)

        # Test
        response = await ObjectService.list_objects(self.bucket)
        self.assertIn(key, response)

        await ObjectService.delete_object(self.bucket, key)

    async def test_upload_object(self):
        data = read_file(self.object_path)
        key = "test_file"
        await ObjectService.upload_object(self.bucket, key, data)

        response = await ObjectService.get_object(self.bucket, key)
        self.assertEqual(data, response)
