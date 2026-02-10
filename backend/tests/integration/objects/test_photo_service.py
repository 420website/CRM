# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportAttributeAccessIssue=none
import asyncio
from datetime import date
from io import BytesIO
from unittest import IsolatedAsyncioTestCase

from fastapi import HTTPException
from app.common.storage.postgres import database
from app.core.objects.object_queries import ObjectService
from app.core.objects.photo_queries import PhotoQueries
from app.core.objects.photo_services import PhotoService
from app.core.objects.schemas import PhotoCreate
from app.core.registration.schemas import PatientCreate
from app.core.registration.services import PatientService
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

        # Test file data
        self.test_file_path = "tests/integration/objects/docs/test-img.jpeg"
        self.test_data = read_file(self.test_file_path)

        # A valid attachment to use
        self.photo_data = PhotoCreate(
            photo_name="test.png",
            photo_key=f"{self.patient_id}/test",
            mime_type="image/jpeg",
        )

    async def asyncTearDown(self) -> None:
        try:
            async with database.get_connection() as conn:
                photo = await PhotoQueries.get_photo(conn, self.patient_id)
            if photo:
                try:
                    await ObjectService.delete_object(
                        "photos", photo.photo_key
                    )
                except Exception:
                    pass
        except Exception:
            pass

        await PatientService.delete_patient("Jim", "Doe")
        await minio_client.disconnect()
        await database.disconnect()

    #### UPLOAD TESTS
    async def test_upload_photo_success(self):
        """Test uploading a new photo"""
        file = BytesIO(self.test_data)

        # Test
        await PhotoService.upload_photo(
            self.patient_id,
            self.photo_data,
            file,
        )

        # Validate - check database record
        async with database.get_connection() as conn:
            photo = await PhotoQueries.get_photo(conn, self.patient_id)

        self.assertIsNotNone(photo)
        self.assertEqual(photo.patient_id, self.patient_id)
        self.assertEqual(photo.photo_name, self.photo_data.photo_name)
        self.assertEqual(photo.photo_key, self.photo_data.photo_key)

        # Validate - check MinIO object exists
        objects = await ObjectService.list_objects("photos")
        self.assertIn(self.photo_data.photo_key, objects)

        # Validate - check MinIO object content
        stored_data = await ObjectService.get_object(
            "photos", self.photo_data.photo_key
        )
        self.assertEqual(stored_data, self.test_data)

    async def test_upload_photo_replaces_old_photo(self):
        """Test that uploading new photo deletes old photo from MinIO"""
        # Upload first photo
        file1 = BytesIO(self.test_data)
        first_photo_data = PhotoCreate(
            photo_name="first.jpg",
            photo_key=f"{self.patient_id}/first.jpg",
            mime_type="image/jpeg",
        )

        await PhotoService.upload_photo(
            self.patient_id,
            first_photo_data,
            file1,
        )

        # Verify first photo exists in MinIO
        objects_before = await ObjectService.list_objects("photos")
        self.assertIn(first_photo_data.photo_key, objects_before)

        # Upload second photo (should replace first)
        file2 = BytesIO(self.test_data)
        second_photo_data = PhotoCreate(
            photo_name="second.jpg",
            photo_key=f"{self.patient_id}/second.jpg",
            mime_type="image/jpeg",
        )

        await PhotoService.upload_photo(
            self.patient_id,
            second_photo_data,
            file2,
        )

        # Validate - old photo deleted from MinIO
        objects_after = await ObjectService.list_objects("photos")
        self.assertNotIn(first_photo_data.photo_key, objects_after)

        # Validate - new photo exists in MinIO
        self.assertIn(second_photo_data.photo_key, objects_after)

        # Validate - database has new photo
        async with database.get_connection() as conn:
            photo = await PhotoQueries.get_photo(conn, self.patient_id)
        self.assertEqual(photo.photo_key, second_photo_data.photo_key)

    async def test_upload_photo_same_key_no_deletion(self):
        """Test that re-uploading with same key doesn't trigger deletion"""
        # Upload first photo
        file1 = BytesIO(self.test_data)
        await PhotoService.upload_photo(
            self.patient_id,
            self.photo_data,
            file1,
        )

        async with database.get_connection() as conn:
            old_photo = await PhotoQueries.get_photo(conn, self.patient_id)

        # Re-upload with same key (e.g., updating metadata)
        file2 = BytesIO(self.test_data)
        same_key_photo = PhotoCreate(
            photo_name="updated_name.jpg",
            photo_key=self.photo_data.photo_key,  # Same key
            mime_type="image/jpeg",
        )

        await PhotoService.upload_photo(
            self.patient_id,
            same_key_photo,
            file2,
        )

        # Validate - photo still exists in MinIO
        objects = await ObjectService.list_objects("photos")
        self.assertIn(self.photo_data.photo_key, objects)

        # Validate - database updated
        async with database.get_connection() as conn:
            new_photo = await PhotoQueries.get_photo(conn, self.patient_id)

        self.assertEqual(new_photo.id, old_photo.id)
        self.assertEqual(new_photo.photo_name, "updated_name.jpg")
        self.assertGreaterEqual(new_photo.uploaded_at, old_photo.uploaded_at)

    async def test_upload_photo_same_key_different_file_data(self):
        """Test that re-uploading same key with different file data replaces the content"""
        # Upload first photo with original data
        original_data = b"original_image_data_12345"
        file1 = BytesIO(original_data)
        await PhotoService.upload_photo(
            self.patient_id,
            self.photo_data,
            file1,
        )

        # Verify original data is stored
        stored_data_before = await ObjectService.get_object(
            "photos", self.photo_data.photo_key
        )
        self.assertEqual(stored_data_before, original_data)

        # Re-upload with DIFFERENT file data but SAME key
        new_data = b"completely_new_image_data_67890"
        file2 = BytesIO(new_data)
        same_key_photo = PhotoCreate(
            photo_name=self.photo_data.photo_name,  # Same name
            photo_key=self.photo_data.photo_key,  # Same key
            mime_type="image/jpeg",
        )

        await PhotoService.upload_photo(
            self.patient_id,
            same_key_photo,
            file2,
        )

        # CRITICAL: Verify MinIO object now contains NEW data, not old data
        stored_data_after = await ObjectService.get_object(
            "photos", self.photo_data.photo_key
        )
        self.assertEqual(stored_data_after, new_data)
        self.assertNotEqual(stored_data_after, original_data)

        # Verify database still has same key
        async with database.get_connection() as conn:
            photo = await PhotoQueries.get_photo(conn, self.patient_id)
        self.assertEqual(photo.photo_key, self.photo_data.photo_key)

        # Verify only one object exists in MinIO (not two)
        objects = await ObjectService.list_objects("photos")
        key_count = sum(
            1 for obj in objects if obj == self.photo_data.photo_key
        )
        self.assertEqual(key_count, 1)

    async def test_upload_photo_same_key_realistic_image_scenario(self):
        """Test realistic scenario: user uploads profile photo, then uploads a better one with same filename"""
        # First upload - user's initial profile photo
        first_image_data = (
            b"\x89PNG\r\n\x1a\n" + b"first_photo_content" + b"x" * 100
        )
        file1 = BytesIO(first_image_data)

        photo_metadata = PhotoCreate(
            photo_name="profile.jpg",
            photo_key=f"{self.patient_id}/profile.jpg",
            mime_type="image/jpeg",
        )

        await PhotoService.upload_photo(
            self.patient_id,
            photo_metadata,
            file1,
        )

        # User retrieves their photo
        data1, _ = await PhotoService.get_photo(self.patient_id)
        self.assertEqual(data1, first_image_data)

        # Second upload - user uploads a BETTER photo but keeps same filename
        second_image_data = (
            b"\x89PNG\r\n\x1a\n" + b"second_better_photo" + b"y" * 100
        )
        file2 = BytesIO(second_image_data)

        # Same metadata (same key!)
        await PhotoService.upload_photo(
            self.patient_id,
            photo_metadata,  # Same photo_key
            file2,
        )

        # User retrieves photo again - should get NEW photo data
        data2, _ = await PhotoService.get_photo(self.patient_id)
        self.assertEqual(data2, second_image_data)
        self.assertNotEqual(data2, first_image_data)

        # Verify the actual MinIO object contains new data
        direct_fetch = await ObjectService.get_object(
            "photos", photo_metadata.photo_key
        )
        self.assertEqual(direct_fetch, second_image_data)
        self.assertNotEqual(direct_fetch, first_image_data)

    #### GET TESTS
    async def test_get_photo_success(self):
        """Test retrieving photo data"""
        # Upload photo first
        file = BytesIO(self.test_data)
        await PhotoService.upload_photo(
            self.patient_id,
            self.photo_data,
            file,
        )

        # Test
        data, name = await PhotoService.get_photo(self.patient_id)

        # Validate
        self.assertEqual(name, self.photo_data.photo_name)
        self.assertEqual(data, self.test_data)

    async def test_get_photo_not_found(self):
        """Test getting photo for patient without photo"""
        with self.assertRaises(HTTPException) as context:
            await PhotoService.get_photo(99999)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(
            context.exception.detail,
            "Photo key not found for patient.",
        )

    async def test_get_patient_photo_key_success(self):
        """Test retrieving just the photo key"""
        # Upload photo first
        file = BytesIO(self.test_data)
        await PhotoService.upload_photo(
            self.patient_id,
            self.photo_data,
            file,
        )

        # Test
        photo_key = await PhotoService.get_patient_photo_key(self.patient_id)

        # Validate
        self.assertEqual(photo_key, self.photo_data.photo_key)

    async def test_get_patient_photo_key_not_found(self):
        """Test getting photo key for patient without photo"""
        key = await PhotoService.get_patient_photo_key(99999)

        self.assertIsNone(key)

    #### DELETE TESTS
    async def test_delete_photo_success(self):
        """Test deleting a photo"""
        # Upload photo first
        file = BytesIO(self.test_data)
        await PhotoService.upload_photo(
            self.patient_id,
            self.photo_data,
            file,
        )

        # Verify it exists in MinIO
        objects_before = await ObjectService.list_objects("photos")
        self.assertIn(self.photo_data.photo_key, objects_before)

        # Test deletion
        await PhotoService.delete_photo(self.patient_id)

        # Validate - check database record deleted
        async with database.get_connection() as conn:
            photo = await PhotoQueries.get_photo(conn, self.patient_id)
        self.assertIsNone(photo)

        # Validate - check MinIO object deleted
        objects_after = await ObjectService.list_objects("photos")
        self.assertNotIn(self.photo_data.photo_key, objects_after)

    async def test_delete_photo_not_found(self):
        """Test deleting photo for patient without photo"""
        with self.assertRaises(HTTPException) as context:
            await PhotoService.delete_photo(99999)

        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(
            context.exception.detail,
            "Error deleting photo metadata.",
        )

    async def test_delete_photo_removes_minio_object(self):
        """Test that deletion removes MinIO object"""
        # Upload photo
        file = BytesIO(self.test_data)
        await PhotoService.upload_photo(
            self.patient_id,
            self.photo_data,
            file,
        )

        # Delete photo
        await PhotoService.delete_photo(self.patient_id)

        # Verify MinIO object is gone
        objects = await ObjectService.list_objects("photos")
        self.assertNotIn(self.photo_data.photo_key, objects)

    #### INTEGRATION TESTS
    async def test_full_photo_lifecycle(self):
        """Test complete upload -> get -> update -> delete workflow"""
        # 1. Upload
        file1 = BytesIO(self.test_data)
        await PhotoService.upload_photo(
            self.patient_id,
            self.photo_data,
            file1,
        )

        # Verify in database
        async with database.get_connection() as conn:
            photo = await PhotoQueries.get_photo(conn, self.patient_id)
        self.assertEqual(photo.photo_key, self.photo_data.photo_key)

        # Verify in MinIO
        objects = await ObjectService.list_objects("photos")
        self.assertIn(self.photo_data.photo_key, objects)

        # 2. Get
        data, name = await PhotoService.get_photo(self.patient_id)
        self.assertEqual(data, self.test_data)
        self.assertEqual(name, self.photo_data.photo_name)

        # 3. Update with new key
        file2 = BytesIO(self.test_data)
        new_photo_data = PhotoCreate(
            photo_name="updated.jpg",
            photo_key=f"{self.patient_id}/updated.jpg",
            mime_type="image/jpeg",
        )
        await PhotoService.upload_photo(
            self.patient_id,
            new_photo_data,
            file2,
        )

        # Verify old photo deleted from MinIO
        objects_after_update = await ObjectService.list_objects("photos")
        self.assertNotIn(self.photo_data.photo_key, objects_after_update)
        self.assertIn(new_photo_data.photo_key, objects_after_update)

        # 4. Delete
        await PhotoService.delete_photo(self.patient_id)

        # Verify deleted from database
        async with database.get_connection() as conn:
            final_photo = await PhotoQueries.get_photo(conn, self.patient_id)
        self.assertIsNone(final_photo)

        # Verify deleted from MinIO
        final_objects = await ObjectService.list_objects("photos")
        self.assertNotIn(new_photo_data.photo_key, final_objects)

    async def test_multiple_patients_isolation(self):
        """Test that photos are properly isolated between patients"""
        # Create second patient
        patient2 = PatientCreate(
            first_name="Jane",
            last_name="Smith",
            dob=date(1985, 5, 15),
            age=38,
            gender="Female",
            health_card="0987654321",
            health_card_version="CD",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
        )
        await PatientService.create_patient(patient2)
        patients = await PatientService.get_patients()
        patient2_id = next(
            (p.id for p in patients if p.first_name == "Jane"), None
        )

        try:
            # Upload photos for both patients
            file1 = BytesIO(self.test_data)
            photo1_data = PhotoCreate(
                photo_name="patient1.jpg",
                photo_key=f"{self.patient_id}/patient1.jpg",
                mime_type="image/jpeg",
            )
            await PhotoService.upload_photo(
                self.patient_id, photo1_data, file1
            )

            file2 = BytesIO(self.test_data)
            photo2_data = PhotoCreate(
                photo_name="patient2.jpg",
                photo_key=f"{patient2_id}/patient2.jpg",
                mime_type="image/jpeg",
            )
            await PhotoService.upload_photo(patient2_id, photo2_data, file2)

            # Verify each patient has their own photo
            _, name1 = await PhotoService.get_photo(self.patient_id)
            _, name2 = await PhotoService.get_photo(patient2_id)

            self.assertEqual(name1, "patient1.jpg")
            self.assertEqual(name2, "patient2.jpg")

            # Verify both exist in MinIO with different keys
            objects = await ObjectService.list_objects("photos")
            self.assertIn(photo1_data.photo_key, objects)
            self.assertIn(photo2_data.photo_key, objects)

            # Delete patient 1 photo shouldn't affect patient 2
            await PhotoService.delete_photo(self.patient_id)

            objects_after = await ObjectService.list_objects("photos")
            self.assertNotIn(photo1_data.photo_key, objects_after)
            self.assertIn(photo2_data.photo_key, objects_after)

            # Patient 2 photo should still be accessible
            data2_after, _ = await PhotoService.get_photo(patient2_id)
            self.assertEqual(data2_after, self.test_data)

        finally:
            # Cleanup patient 2
            try:
                await PhotoService.delete_photo(patient2_id)
            except Exception:
                pass
            await PatientService.delete_patient("Jane", "Smith")

    async def test_concurrent_photo_updates(self):
        """Test that concurrent updates handle old photo cleanup correctly"""
        # Upload initial photo
        file1 = BytesIO(self.test_data)
        first_photo_data = PhotoCreate(
            photo_name="first.jpg",
            photo_key=f"{self.patient_id}/first.jpg",
            mime_type="image/jpeg",
        )
        await PhotoService.upload_photo(
            self.patient_id, first_photo_data, file1
        )

        # Upload second photo (should clean up first)
        file2 = BytesIO(self.test_data)
        second_photo_data = PhotoCreate(
            photo_name="second.jpg",
            photo_key=f"{self.patient_id}/second.jpg",
            mime_type="image/jpeg",
        )
        await PhotoService.upload_photo(
            self.patient_id, second_photo_data, file2
        )

        # Upload third photo (should clean up second)
        file3 = BytesIO(self.test_data)
        third_photo_data = PhotoCreate(
            photo_name="third.jpg",
            photo_key=f"{self.patient_id}/third.jpg",
            mime_type="image/jpeg",
        )
        await PhotoService.upload_photo(
            self.patient_id, third_photo_data, file3
        )

        # Verify only the latest photo exists in MinIO
        objects = await ObjectService.list_objects("photos")
        self.assertNotIn(first_photo_data.photo_key, objects)
        self.assertNotIn(second_photo_data.photo_key, objects)
        self.assertIn(third_photo_data.photo_key, objects)

        # Verify database has latest photo
        async with database.get_connection() as conn:
            photo = await PhotoQueries.get_photo(conn, self.patient_id)
        self.assertEqual(photo.photo_key, third_photo_data.photo_key)


# -- old delete ---
#
# async def test_upload_photo_success(self):
#     result = await PhotoService.upload_photo(
#         self.patient_id,
#         self.photo,
#     )
#     self.assertTrue(result)
#
# async def test_update_photo_success(self):
#     id = await PhotoService.upload_photo(
#         self.patient_id,
#         self.photo,
#     )
#
#     self.photo.photo_name = "new_name"
#
#     # test
#     result = await PhotoService.upload_photo(self.patient_id, self.photo)
#     self.assertEqual(id, result)
#
#     # test
#     photo = await PhotoService.get_photo(self.patient_id)
#     self.assertEqual(photo.photo_name, "new_name")
#
# async def test_update_photo_same_name(self):
#     self.photo.photo_name = "name_123"
#     await PhotoService.upload_photo(self.patient_id, self.photo)
#     old_photo = await PhotoService.get_photo(self.patient_id)
#
#     # test
#     await PhotoService.upload_photo(self.patient_id, self.photo)
#     new_photo = await PhotoService.get_photo(self.patient_id)
#
#     self.assertEqual(old_photo.id, new_photo.id)
#     self.assertEqual(old_photo.patient_id, new_photo.patient_id)
#     self.assertEqual(old_photo.photo_key, new_photo.photo_key)
#     self.assertGreaterEqual(new_photo.uploaded_at, old_photo.uploaded_at)
#
# async def test_update_photo_different_name(self):
#     self.photo.photo_name = "name_123"
#     self.photo.photo_key = "13784/name_123"
#     await PhotoService.upload_photo(self.patient_id, self.photo)
#     old_photo = await PhotoService.get_photo(self.patient_id)
#
#     # test
#     self.photo.photo_name = "name_1234"
#     self.photo.photo_key = "13784/name_1234"
#     await PhotoService.upload_photo(self.patient_id, self.photo)
#     new_photo = await PhotoService.get_photo(self.patient_id)
#
#     self.assertEqual(old_photo.id, new_photo.id)
#     self.assertEqual(old_photo.patient_id, new_photo.patient_id)
#     self.assertNotEqual(old_photo.photo_key, new_photo.photo_key)
#     self.assertGreaterEqual(new_photo.uploaded_at, old_photo.uploaded_at)
#
# async def test_get_photo_key(self):
#     await PhotoService.upload_photo(
#         self.patient_id,
#         self.photo,
#     )
#
#     photo_key = await PhotoService.get_patient_photo_key(self.patient_id)
#     self.assertEqual(photo_key, self.photo.photo_key)
#
# async def test_get_photo_success(self):
#     await PhotoService.upload_photo(
#         self.patient_id,
#         self.photo,
#     )
#
#     photo = await PhotoService.get_photo(self.patient_id)
#     self.assertEqual(photo.patient_id, self.patient_id)
#     self.assertEqual(photo.photo_name, self.photo.photo_name)
#     self.assertEqual(photo.photo_key, self.photo.photo_key)
#
# async def test_delete_photo_success(self):
#     await PhotoService.upload_photo(
#         self.patient_id,
#         self.photo,
#     )
#
#     result = await PhotoService.delete_photo(self.patient_id)
#     self.assertTrue(result)
#
#     photo = await PhotoService.get_photo(self.patient_id)
#     self.assertIsNone(photo)
