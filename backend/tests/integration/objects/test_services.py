# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportAttributeAccessIssue=none
import asyncio
from datetime import date
from unittest import IsolatedAsyncioTestCase
from app.common.storage.postgres import database
from app.common.storage.minio import minio_client
from app.core.objects.schemas import AttachmentCreate, PhotoCreate
from app.core.registration.schemas import PatientCreate
from app.core.registration.services import PatientService
from app.core.objects.services import (
    AttachmentService,
    ObjectService,
    PhotoService,
)


def read_file(path: str) -> bytes:
    with open(path, "rb") as file:
        file_bytes = file.read()
        return file_bytes


# -------------
# Object Tests
# -------------
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
        await minio_client.connect()

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


# ------------
# Photo Tests
# ------------
class TestPhotoServices(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()

        # Ensure no leftover patients
        await PatientService.delete_patient("Jim", "Doe")

        # Create a minimal patient for linking attachments
        self.minimal_patient = PatientCreate(
            first_name="Jim",
            last_name="Doe",
            dob=date(1990, 3, 22),
            age=30,
            gender="Male",
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
        )
        await PatientService.create_patient(self.minimal_patient)
        patients = await PatientService.get_patients()
        self.patient_id = patients[0].id

        # A valid attachment to use
        self.photo = PhotoCreate(
            photo_name="test.png",
            photo_key=f"{self.patient_id}/test",
        )

    async def asyncTearDown(self) -> None:
        await PatientService.delete_patient("Jim", "Doe")
        await database.disconnect()

    async def test_upload_photo_success(self):
        result = await PhotoService.upload_photo(
            self.patient_id,
            self.photo,
        )
        self.assertTrue(result)

    async def test_update_photo_success(self):
        id = await PhotoService.upload_photo(
            self.patient_id,
            self.photo,
        )

        self.photo.photo_name = "new_name"

        # test
        result = await PhotoService.upload_photo(self.patient_id, self.photo)
        self.assertEqual(id, result)

        # test
        photo = await PhotoService.get_photo(self.patient_id)
        self.assertEqual(photo.photo_name, "new_name")

    async def test_update_photo_same_name(self):
        self.photo.photo_name = "name_123"
        await PhotoService.upload_photo(self.patient_id, self.photo)
        old_photo = await PhotoService.get_photo(self.patient_id)

        # test
        await PhotoService.upload_photo(self.patient_id, self.photo)
        new_photo = await PhotoService.get_photo(self.patient_id)

        self.assertEqual(old_photo.id, new_photo.id)
        self.assertEqual(old_photo.patient_id, new_photo.patient_id)
        self.assertEqual(old_photo.photo_key, new_photo.photo_key)
        self.assertGreaterEqual(new_photo.uploaded_at, old_photo.uploaded_at)

    async def test_update_photo_different_name(self):
        self.photo.photo_name = "name_123"
        self.photo.photo_key = "13784/name_123"
        await PhotoService.upload_photo(self.patient_id, self.photo)
        old_photo = await PhotoService.get_photo(self.patient_id)

        # test
        self.photo.photo_name = "name_1234"
        self.photo.photo_key = "13784/name_1234"
        await PhotoService.upload_photo(self.patient_id, self.photo)
        new_photo = await PhotoService.get_photo(self.patient_id)

        self.assertEqual(old_photo.id, new_photo.id)
        self.assertEqual(old_photo.patient_id, new_photo.patient_id)
        self.assertNotEqual(old_photo.photo_key, new_photo.photo_key)
        self.assertGreaterEqual(new_photo.uploaded_at, old_photo.uploaded_at)

    async def test_get_photo_key(self):
        await PhotoService.upload_photo(
            self.patient_id,
            self.photo,
        )

        photo_key = await PhotoService.get_patient_photo_key(self.patient_id)
        self.assertEqual(photo_key, self.photo.photo_key)

    async def test_get_photo_success(self):
        await PhotoService.upload_photo(
            self.patient_id,
            self.photo,
        )

        photo = await PhotoService.get_photo(self.patient_id)
        self.assertEqual(photo.patient_id, self.patient_id)
        self.assertEqual(photo.photo_name, self.photo.photo_name)
        self.assertEqual(photo.photo_key, self.photo.photo_key)

    async def test_delete_photo_success(self):
        await PhotoService.upload_photo(
            self.patient_id,
            self.photo,
        )

        result = await PhotoService.delete_photo(self.patient_id)
        self.assertTrue(result)

        photo = await PhotoService.get_photo(self.patient_id)
        self.assertIsNone(photo)


# ----------------
# Attachment Tests
# _______________
class TestAttachmentsService(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()

        # Ensure no leftover patients
        await PatientService.delete_patient("Jim", "Doe")

        # Create a minimal patient for linking attachments
        self.minimal_patient = PatientCreate(
            first_name="Jim",
            last_name="Doe",
            dob=date(1990, 3, 22),
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )

        await PatientService.create_patient(self.minimal_patient)
        patients = await PatientService.get_patients()
        self.patient_id = patients[0].id

        # A valid attachment to use
        self.key = f"{self.patient_id}/test_document.pdf"
        self.attachment_data = AttachmentCreate(
            file_name="test_document.pdf",
            file_key=self.key,
            file_size=1024,
            mime_type="application/pdf",
            document_type="consultation report",
        )

    async def asyncTearDown(self) -> None:
        await PatientService.delete_patient("Jim", "Doe")
        await database.disconnect()

    async def test_upload_attachment_success(self):
        result = await AttachmentService.upload_attachment(
            self.patient_id,
            self.attachment_data,
        )
        self.assertTrue(result)

        # Validate
        attachments = await AttachmentService.get_patient_attachments(
            self.patient_id
        )
        self.assertGreaterEqual(len(attachments), 1)

    async def test_upload_attachment_overwrite(self):
        # Upload attachment
        result = await AttachmentService.upload_attachment(
            self.patient_id,
            self.attachment_data,
        )
        self.assertTrue(result)

        # Create new with the same name/id
        self.attachment_data.mime_type = "image/jpeg"
        attachments = await AttachmentService.upload_attachment(
            self.patient_id,
            self.attachment_data,
        )

        # Validate
        attachments = await AttachmentService.get_patient_attachments(
            self.patient_id
        )
        self.assertEqual(len(attachments), 1)
        self.assertEqual(
            attachments[0].file_name,
            self.attachment_data.file_name,
        )

    #### GET
    async def test_get_attachments_empty(self):
        attachments = await AttachmentService.get_patient_attachments(
            self.patient_id
        )

        self.assertIsInstance(attachments, list)
        self.assertEqual(len(attachments), 0)

    async def test_get_attachments(self):
        result = await AttachmentService.upload_attachment(
            self.patient_id,
            self.attachment_data,
        )
        self.assertTrue(result)

        attachments = await AttachmentService.get_patient_attachments(
            self.patient_id
        )

        self.assertEqual(len(attachments), 1)
        self.assertEqual(
            attachments[0].file_name, self.attachment_data.file_name
        )

    async def test_get_attachment(self):
        result = await AttachmentService.upload_attachment(
            self.patient_id,
            self.attachment_data,
        )
        self.assertTrue(result)

        attachment = await AttachmentService.get_attachment(
            self.patient_id,
            self.attachment_data.file_name,
        )

        self.assertEqual(attachment.file_name, self.attachment_data.file_name)
        self.assertEqual(attachment.file_size, self.attachment_data.file_size)
        self.assertEqual(attachment.file_key, self.attachment_data.file_key)

    async def test_get_attachment_none(self):
        attachment = await AttachmentService.get_attachment(
            self.patient_id, self.attachment_data.file_name
        )
        self.assertIsNone(attachment)

    async def test_get_attachment_by_id(self):
        id = await AttachmentService.upload_attachment(
            self.patient_id,
            self.attachment_data,
        )
        self.assertTrue(id)

        attachment = await AttachmentService.get_attachment_by_id(id)
        self.assertEqual(attachment.file_name, self.attachment_data.file_name)
        self.assertEqual(attachment.file_size, self.attachment_data.file_size)
        self.assertEqual(attachment.file_key, self.attachment_data.file_key)

    #### DELETE
    async def test_delete_attachment_by_id_success(self):
        await AttachmentService.upload_attachment(
            self.patient_id,
            self.attachment_data,
        )
        attachments = await AttachmentService.get_patient_attachments(
            self.patient_id
        )
        attachment_id = attachments[0].id

        # Test
        result = await AttachmentService.delete_attachment_by_id(attachment_id)
        self.assertTrue(result)

        # Validate
        remaining = await AttachmentService.get_patient_attachments(
            self.patient_id
        )
        self.assertEqual(len(remaining), 0)

    async def test_delete_attachment_by_id_not_found(self):
        result = await AttachmentService.delete_attachment_by_id(9999)
        self.assertFalse(result)

    async def test_delete_attachment_success(self):
        id = await AttachmentService.upload_attachment(
            self.patient_id,
            self.attachment_data,
        )
        self.assertTrue(id)

        # Test
        result = await AttachmentService.delete_attachment(
            self.patient_id,
            self.attachment_data.file_name,
        )
        self.assertTrue(result)

        # Validate
        remaining = await AttachmentService.get_patient_attachments(
            self.patient_id
        )
        self.assertEqual(len(remaining), 0)

    async def test_delete_attachment_not_found(self):
        result = await AttachmentService.delete_attachment(
            self.patient_id,
            self.attachment_data.file_name,
        )
        self.assertFalse(result)
