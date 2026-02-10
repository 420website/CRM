# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportAttributeAccessIssue=none
import asyncio
from datetime import date
from unittest import IsolatedAsyncioTestCase
from app.common.storage.postgres import database
from app.core.objects.photo_queries import PhotoQueries
from app.core.objects.schemas import PhotoCreate
from app.core.registration.schemas import PatientCreate
from app.core.registration.services import PatientService


def read_file(path: str) -> bytes:
    with open(path, "rb") as file:
        file_bytes = file.read()
        return file_bytes


class TestPhotoQueries(IsolatedAsyncioTestCase):
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
        self.photo_data = PhotoCreate(
            photo_name="test.png",
            photo_key=f"{self.patient_id}/test",
            mime_type="image/jpeg",
        )

    async def asyncTearDown(self) -> None:
        await PatientService.delete_patient("Jim", "Doe")
        await database.disconnect()

    #### UPLOAD/UPSERT TESTS
    async def test_upload_photo_success(self):
        """Test uploading a new photo"""
        async with database.get_transaction() as conn:
            old_key = await PhotoQueries.upload_photo(
                conn,
                self.patient_id,
                self.photo_data,
            )

        # Should return None for first upload (no old key)
        self.assertIsNone(old_key)

        # Validate photo was saved
        async with database.get_connection() as conn:
            photo = await PhotoQueries.get_photo(conn, self.patient_id)

        self.assertIsNotNone(photo)
        self.assertEqual(photo.patient_id, self.patient_id)
        self.assertEqual(photo.photo_name, self.photo_data.photo_name)
        self.assertEqual(photo.photo_key, self.photo_data.photo_key)

    async def test_update_photo_same_key(self):
        """Test updating photo with same key (no old_key returned)"""
        # Upload initial photo
        async with database.get_transaction() as conn:
            old_key = await PhotoQueries.upload_photo(
                conn,
                self.patient_id,
                self.photo_data,
            )
        self.assertIsNone(old_key)

        # Get initial photo
        async with database.get_connection() as conn:
            old_photo = await PhotoQueries.get_photo(conn, self.patient_id)

        # Update with same key, different name
        updated_photo_data = PhotoCreate(
            photo_name="updated_name.png",
            photo_key=self.photo_data.photo_key,
            mime_type="image/jpeg",
        )

        async with database.get_transaction() as conn:
            returned_old_key = await PhotoQueries.upload_photo(
                conn,
                self.patient_id,
                updated_photo_data,
            )

        # Should return None since key didn't change
        self.assertIsNone(returned_old_key)

        # Validate update
        async with database.get_connection() as conn:
            new_photo = await PhotoQueries.get_photo(conn, self.patient_id)

        self.assertEqual(new_photo.id, old_photo.id)
        self.assertEqual(new_photo.photo_name, "updated_name.png")
        self.assertEqual(new_photo.photo_key, self.photo_data.photo_key)
        self.assertGreaterEqual(new_photo.uploaded_at, old_photo.uploaded_at)

    async def test_update_photo_different_key(self):
        """Test updating photo with different key (returns old_key)"""
        # Upload initial photo
        async with database.get_transaction() as conn:
            await PhotoQueries.upload_photo(
                conn,
                self.patient_id,
                self.photo_data,
            )

        # Get initial photo
        async with database.get_connection() as conn:
            old_photo = await PhotoQueries.get_photo(conn, self.patient_id)

        old_key = old_photo.photo_key

        # Update with different key
        new_photo_data = PhotoCreate(
            photo_name="new_photo.png",
            photo_key=f"{self.patient_id}/new_photo.png",
            mime_type="image/jpeg",
        )

        async with database.get_transaction() as conn:
            returned_old_key = await PhotoQueries.upload_photo(
                conn,
                self.patient_id,
                new_photo_data,
            )

        # Should return the old key for cleanup
        self.assertEqual(returned_old_key, old_key)

        # Validate update
        async with database.get_connection() as conn:
            new_photo = await PhotoQueries.get_photo(conn, self.patient_id)

        self.assertEqual(new_photo.id, old_photo.id)  # Same record
        self.assertEqual(new_photo.photo_name, "new_photo.png")
        self.assertEqual(new_photo.photo_key, new_photo_data.photo_key)
        self.assertNotEqual(new_photo.photo_key, old_key)

    async def test_upload_photo_upsert_behavior(self):
        """Test that upload_photo properly upserts (insert or update)"""
        # First upload
        async with database.get_transaction() as conn:
            await PhotoQueries.upload_photo(
                conn,
                self.patient_id,
                self.photo_data,
            )

        async with database.get_connection() as conn:
            photo1 = await PhotoQueries.get_photo(conn, self.patient_id)

        # photo_id_1 = photo1.id

        # Second upload (should update, not insert)
        updated_data = PhotoCreate(
            photo_name="updated.png",
            photo_key=f"{self.patient_id}/updated.png",
            mime_type="image/jpeg",
        )

        async with database.get_transaction() as conn:
            await PhotoQueries.upload_photo(
                conn,
                self.patient_id,
                updated_data,
            )

        async with database.get_connection() as conn:
            photo2 = await PhotoQueries.get_photo(conn, self.patient_id)

        # Should be same ID (update, not insert)
        self.assertEqual(photo1.id, photo2.id)
        self.assertEqual(photo2.photo_name, "updated.png")

    #### GET TESTS
    async def test_get_photo_success(self):
        """Test retrieving photo metadata"""
        # Upload photo first
        async with database.get_transaction() as conn:
            await PhotoQueries.upload_photo(
                conn,
                self.patient_id,
                self.photo_data,
            )

        # Test
        async with database.get_connection() as conn:
            photo = await PhotoQueries.get_photo(conn, self.patient_id)

        # Validate
        self.assertIsNotNone(photo)
        self.assertEqual(photo.patient_id, self.patient_id)
        self.assertEqual(photo.photo_name, self.photo_data.photo_name)
        self.assertEqual(photo.photo_key, self.photo_data.photo_key)
        self.assertIsNotNone(photo.uploaded_at)

    async def test_get_photo_not_found(self):
        """Test getting photo for patient without photo"""
        async with database.get_connection() as conn:
            photo = await PhotoQueries.get_photo(conn, 99999)

        self.assertIsNone(photo)

    async def test_get_patient_photo_key_success(self):
        """Test retrieving just the photo key"""
        # Upload photo first
        async with database.get_transaction() as conn:
            await PhotoQueries.upload_photo(
                conn,
                self.patient_id,
                self.photo_data,
            )

        # Test
        async with database.get_connection() as conn:
            photo_key = await PhotoQueries.get_patient_photo_key(
                conn, self.patient_id
            )

        # Validate
        self.assertEqual(photo_key, self.photo_data.photo_key)

    async def test_get_patient_photo_key_not_found(self):
        """Test getting photo key for patient without photo"""
        async with database.get_connection() as conn:
            photo_key = await PhotoQueries.get_patient_photo_key(conn, 99999)

        self.assertIsNone(photo_key)

    #### DELETE TESTS
    async def test_delete_photo_success(self):
        """Test deleting a photo"""
        # Upload photo first
        async with database.get_transaction() as conn:
            await PhotoQueries.upload_photo(
                conn,
                self.patient_id,
                self.photo_data,
            )

        # Verify it exists
        async with database.get_connection() as conn:
            photo_before = await PhotoQueries.get_photo(conn, self.patient_id)
        self.assertIsNotNone(photo_before)

        # Test deletion
        async with database.get_transaction() as conn:
            deleted_key = await PhotoQueries.delete_photo(
                conn, self.patient_id
            )

        # Validate returned key
        self.assertEqual(deleted_key, self.photo_data.photo_key)

        # Validate photo is deleted
        async with database.get_connection() as conn:
            photo_after = await PhotoQueries.get_photo(conn, self.patient_id)
        self.assertIsNone(photo_after)

    async def test_delete_photo_not_found(self):
        """Test deleting photo for patient without photo"""
        async with database.get_transaction() as conn:
            deleted_key = await PhotoQueries.delete_photo(conn, 99999)

        self.assertIsNone(deleted_key)

    async def test_delete_photo_idempotent(self):
        """Test that deleting twice doesn't cause issues"""
        # Upload photo
        async with database.get_transaction() as conn:
            await PhotoQueries.upload_photo(
                conn,
                self.patient_id,
                self.photo_data,
            )

        # First delete
        async with database.get_transaction() as conn:
            key1 = await PhotoQueries.delete_photo(conn, self.patient_id)
        self.assertIsNotNone(key1)

        # Second delete
        async with database.get_transaction() as conn:
            key2 = await PhotoQueries.delete_photo(conn, self.patient_id)
        self.assertIsNone(key2)

    #### INTEGRATION TESTS
    async def test_full_photo_lifecycle(self):
        """Test complete upload -> get -> update -> delete workflow"""
        # 1. Upload
        async with database.get_transaction() as conn:
            old_key = await PhotoQueries.upload_photo(
                conn,
                self.patient_id,
                self.photo_data,
            )
        self.assertIsNone(old_key)

        # 2. Get
        async with database.get_connection() as conn:
            photo = await PhotoQueries.get_photo(conn, self.patient_id)
        self.assertEqual(photo.photo_key, self.photo_data.photo_key)

        # 3. Update with new key
        new_photo_data = PhotoCreate(
            photo_name="updated.png",
            photo_key=f"{self.patient_id}/updated.png",
            mime_type="image/jpeg",
        )
        async with database.get_transaction() as conn:
            returned_old_key = await PhotoQueries.upload_photo(
                conn,
                self.patient_id,
                new_photo_data,
            )
        self.assertEqual(returned_old_key, self.photo_data.photo_key)

        # 4. Verify update
        async with database.get_connection() as conn:
            updated_photo = await PhotoQueries.get_photo(conn, self.patient_id)
        self.assertEqual(updated_photo.photo_key, new_photo_data.photo_key)

        # 5. Delete
        async with database.get_transaction() as conn:
            deleted_key = await PhotoQueries.delete_photo(
                conn, self.patient_id
            )
        self.assertEqual(deleted_key, new_photo_data.photo_key)

        # 6. Verify deletion
        async with database.get_connection() as conn:
            final_photo = await PhotoQueries.get_photo(conn, self.patient_id)
        self.assertIsNone(final_photo)

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
            photo1_data = PhotoCreate(
                photo_name="patient1.png",
                photo_key=f"{self.patient_id}/patient1.png",
                mime_type="image/jpeg",
            )
            photo2_data = PhotoCreate(
                photo_name="patient2.png",
                photo_key=f"{patient2_id}/patient2.png",
                mime_type="image/jpeg",
            )

            async with database.get_transaction() as conn:
                await PhotoQueries.upload_photo(
                    conn, self.patient_id, photo1_data
                )
            async with database.get_transaction() as conn:
                await PhotoQueries.upload_photo(conn, patient2_id, photo2_data)

            # Verify each patient has their own photo
            async with database.get_connection() as conn:
                p1_photo = await PhotoQueries.get_photo(conn, self.patient_id)
                p2_photo = await PhotoQueries.get_photo(conn, patient2_id)

            self.assertEqual(p1_photo.photo_name, "patient1.png")
            self.assertEqual(p2_photo.photo_name, "patient2.png")
            self.assertNotEqual(p1_photo.photo_key, p2_photo.photo_key)

        finally:
            # Cleanup patient 2
            await PatientService.delete_patient("Jane", "Smith")


# -- delete  old ---
# async def test_upload_photo_success(self):
#     result = await PhotoService.upload_photo(
#         self.patient_id,
#         self.photo,
#     )
#     self.assertTrue(result)
#
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
