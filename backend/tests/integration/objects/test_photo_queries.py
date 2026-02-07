# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportAttributeAccessIssue=none
import asyncio
from datetime import date
from unittest import IsolatedAsyncioTestCase
from app.common.storage.postgres import database
from app.core.objects.object_queries import ObjectService
from app.core.objects.schemas import PhotoCreate
from app.core.registration.schemas import PatientCreate
from app.core.registration.services import PatientService
from app.core.objects.services import PhotoService
from app.common.storage.minio import minio_client


def read_file(path: str) -> bytes:
    with open(path, "rb") as file:
        file_bytes = file.read()
        return file_bytes


class TestPhotoServices(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()
        await minio_client.connect()

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
        await ObjectService.delete_object("photo", "test_file")
        await ObjectService.delete_bucket("testing")
        await minio_client.disconnect()

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
