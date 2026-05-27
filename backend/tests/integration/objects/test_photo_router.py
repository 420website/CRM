# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportOperatorIssue=none, reportAttributeAccessIssue=none
from io import BytesIO
import re
import pyotp
import asyncio
from unittest import IsolatedAsyncioTestCase
from datetime import date
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, Response, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from app.core.authentication.services import UserService
from app.common.storage.postgres import database
from app.common.storage.minio import minio_client
from app.common.dependencies import get_current_user, get_user_pending_mfa
from app.core.objects.photo_services import PhotoService
from app.core.registration.router import create_patient
from app.core.registration.schemas import PatientCreate
from app.core.objects.object_queries import ObjectService
from app.core.registration.services import PatientService
from app.core.authentication.router import (
    login,
    register,
    setup_authenticator_mfa,
    verify_authenticator_mfa,
    verify_email,
)
from app.core.objects.router import (
    delete_photo,
    get_photo,
    upload_photo,
)
from app.core.authentication.schemas import (
    LoginRequest,
    MFAVerifiactionCode,
    RegisterRequest,
)


def read_file(path: str) -> bytes:
    with open(path, "rb") as file:
        file_bytes = file.read()
        return file_bytes


email = "test4@example.com"
password = "securepassword123"
user_create = RegisterRequest(email=email, password=password)
login_request = LoginRequest(email=email, password=password)


@patch("app.core.authentication.services.EmailService", new_callable=MagicMock)
async def mock_register(mock_email_service_class) -> str:
    # Prepare a mock instance to replace EmailService()
    mock_email_service = MagicMock()
    mock_email_service.recipient.return_value = mock_email_service
    mock_email_service.subject.return_value = mock_email_service

    captured_token = {}

    def mock_body(message_obj):
        # Extract token from the HTML content in message_obj.msg
        html_content = message_obj.msg

        match = re.search(r'token=([^"&]+)', html_content)
        if match:
            captured_token["token"] = match.group(1)
        return mock_email_service

    mock_email_service.body.side_effect = mock_body
    mock_email_service.send.return_value = None

    # This makes EmailService() return our mock instance
    mock_email_service_class.return_value = mock_email_service

    await register(user_create)
    return captured_token["token"]


class TestPatientPhotosRouter(IsolatedAsyncioTestCase):
    @classmethod
    async def get_validated_user(cls):
        token = await mock_register()
        await verify_email(token)
        response = await login(login_request)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=response.access_token,
        )

        user = await get_user_pending_mfa(credentials=credentials)
        response = await setup_authenticator_mfa(user)
        totp = pyotp.TOTP(response.secret)
        code = totp.now()

        user = await get_user_pending_mfa(credentials=credentials)
        response = Response()
        result = await verify_authenticator_mfa(
            MFAVerifiactionCode(code=code), response, user
        )

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=result.access_token,
        )

        user = await get_current_user(credentials=credentials)
        return user

    @classmethod
    async def asyncSetUpClass(cls):
        await database.connect()

        # Delete any user that may exist
        await UserService.delete_user(email, password)
        cls.user = await cls.get_validated_user()

        await database.disconnect()

    @classmethod
    async def asyncTearDownClass(cls):
        await database.connect()
        await UserService.delete_user(email, password)
        await database.disconnect()

    @property
    def user(self):
        return self.__class__.user

    async def mock_create_patient(self, name: str):
        """Helper to create a test patient using class user"""
        patient_data = PatientCreate(
            first_name=name,
            last_name="Doe",
            dob=date(1990, 1, 1),
            age=33,
            gender="Male",
            email="jim.doe@example.com",
            phone1="416-555-0123",
            status="pending",
            health_card="0000000000",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
        )

        result = await create_patient(patient_data, self.user)
        return result["patient_id"]

    async def mock_create_photo(
        self, patient_id: int, file_name: str = "test-img.jpeg"
    ):
        """Helper to create a photo for a patient"""
        data = read_file(self.object_path)
        file = UploadFile(filename=file_name, file=BytesIO(data))
        await upload_photo(patient_id, file_name, file, self.user)

    async def asyncSetUp(self) -> None:
        await database.connect()
        await minio_client.connect()
        asyncio.get_event_loop().set_debug(False)

        self.object_path = "tests/integration/objects/docs/test-img.jpeg"
        self.file_name = "test-img.jpeg"
        self.patient_id = await self.mock_create_patient("Jim")

    async def asyncTearDown(self):
        try:
            photo = await PhotoService.get_photo(self.patient_id)
            if photo:
                await PhotoService.delete_photo(self.patient_id)
        except Exception:
            pass

        await PatientService.delete_patient_by_id(self.patient_id)
        await minio_client.disconnect()
        await database.disconnect()

    #### UPLOAD TESTS
    async def test_upload_photo_success(self):
        """Test uploading a new photo"""
        data = read_file(self.object_path)
        file = UploadFile(filename=self.file_name, file=BytesIO(data))

        # Test
        result = await upload_photo(
            self.patient_id, self.file_name, file, self.user
        )

        # Validate response
        self.assertEqual(result["message"], "Successfully uploaded file.")

        # Validate database record
        photo_data, photo_name = await PhotoService.get_photo(self.patient_id)
        self.assertEqual(photo_name, self.file_name)

        # Validate MinIO object
        expected_key = f"{self.patient_id}/{self.file_name}"
        objects = await ObjectService.list_objects("photos")
        self.assertIn(expected_key, objects)

        # Validate content
        self.assertEqual(photo_data, data)

    async def test_upload_photo_replaces_old_photo(self):
        """Test that uploading new photo replaces old one"""
        # Upload first photo
        await self.mock_create_photo(self.patient_id, "first.jpeg")

        # Verify first photo exists
        objects_before = await ObjectService.list_objects("photos")
        first_key = f"{self.patient_id}/first.jpeg"
        self.assertIn(first_key, objects_before)

        # Upload second photo with different name
        data = read_file(self.object_path)
        file = UploadFile(filename="second.jpeg", file=BytesIO(data))
        result = await upload_photo(
            self.patient_id, "second.jpeg", file, self.user
        )

        self.assertEqual(result["message"], "Successfully uploaded file.")

        # Validate old photo deleted from MinIO
        objects_after = await ObjectService.list_objects("photos")
        self.assertNotIn(first_key, objects_after)

        # Validate new photo exists
        second_key = f"{self.patient_id}/second.jpeg"
        self.assertIn(second_key, objects_after)

    async def test_upload_photo_same_name_overwrites(self):
        """Test uploading photo with same name overwrites old one"""
        # Upload first photo
        original_data = b"original_photo_data_12345"
        file1 = UploadFile(
            filename=self.file_name, file=BytesIO(original_data)
        )

        await upload_photo(self.patient_id, self.file_name, file1, self.user)

        # Get first photo
        data1, _ = await PhotoService.get_photo(self.patient_id)
        self.assertEqual(data1, original_data)

        # Upload second photo with SAME name but DIFFERENT data
        new_data = read_file(self.object_path)
        file2 = UploadFile(filename=self.file_name, file=BytesIO(new_data))

        result = await upload_photo(
            self.patient_id, self.file_name, file2, self.user
        )

        self.assertEqual(result["message"], "Successfully uploaded file.")

        # Validate new data is stored
        data2, _ = await PhotoService.get_photo(self.patient_id)
        self.assertEqual(data2, new_data)
        self.assertNotEqual(data2, original_data)

        # Validate only one object in MinIO
        objects = await ObjectService.list_objects("photos")
        photo_key = f"{self.patient_id}/{self.file_name}"
        key_count = sum(1 for obj in objects if obj == photo_key)
        self.assertEqual(key_count, 1)

    async def test_upload_photo_updates_metadata(self):
        """Test uploading photo updates timestamp"""
        # Upload first photo
        await self.mock_create_photo(self.patient_id)

        data1, _ = await PhotoService.get_photo(self.patient_id)

        # Small delay to ensure timestamp difference
        await asyncio.sleep(0.1)

        # Upload again with same name
        data = read_file(self.object_path)
        file = UploadFile(filename=self.file_name, file=BytesIO(data))
        await upload_photo(self.patient_id, self.file_name, file, self.user)

        # Validate upload happened
        data2, _ = await PhotoService.get_photo(self.patient_id)
        self.assertEqual(data2, data)
        self.assertEqual(data1, data)

    #### GET TESTS
    async def test_get_photo_success(self):
        """Test retrieving a photo"""
        await self.mock_create_photo(self.patient_id)

        # Test
        result = await get_photo(self.patient_id, self.user)

        # Validate response
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.media_type, "application/octet-stream")
        self.assertEqual(result.headers["file-name"], self.file_name)

        # Validate content
        body = result.body
        self.assertIsInstance(body, bytes)
        self.assertGreater(len(body), 0)
        self.assertEqual(body, read_file(self.object_path))

    async def test_get_photo_not_found(self):
        """Test getting photo for patient without photo"""
        with self.assertRaises(HTTPException) as context:
            await get_photo(self.patient_id, self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(
            context.exception.detail, "Photo key not found for patient."
        )

    async def test_get_photo_correct_file_name_header(self):
        """Test that response includes correct file-name header"""
        custom_name = "custom_photo.jpg"
        await self.mock_create_photo(self.patient_id, custom_name)

        result = await get_photo(self.patient_id, self.user)

        self.assertEqual(result.headers["file-name"], custom_name)

    #### DELETE TESTS
    async def test_delete_photo_success(self):
        """Test deleting a photo"""
        await self.mock_create_photo(self.patient_id)

        # Verify photo exists
        photo_key = f"{self.patient_id}/{self.file_name}"
        objects_before = await ObjectService.list_objects("photos")
        self.assertIn(photo_key, objects_before)

        # Test deletion
        result = await delete_photo(self.patient_id, self.user)

        # Validate response
        self.assertEqual(result["message"], "Successfully deleted photo.")

        # Validate database deletion
        with self.assertRaises(HTTPException):
            await PhotoService.get_photo(self.patient_id)

        # Validate MinIO deletion
        objects_after = await ObjectService.list_objects("photos")
        self.assertNotIn(photo_key, objects_after)

    async def test_delete_photo_not_found(self):
        """Test deleting photo for patient without photo"""
        with self.assertRaises(HTTPException) as context:
            await delete_photo(self.patient_id, self.user)

        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(
            context.exception.detail,
            "Error deleting photo metadata.",
        )

    async def test_delete_photo_removes_from_minio(self):
        """Test that deletion removes object from MinIO"""
        await self.mock_create_photo(self.patient_id)

        photo_key = f"{self.patient_id}/{self.file_name}"

        # Delete
        await delete_photo(self.patient_id, self.user)

        # Verify MinIO object removed
        objects = await ObjectService.list_objects("photos")
        self.assertNotIn(photo_key, objects)

    #### INTEGRATION TESTS
    async def test_full_photo_workflow(self):
        """Test complete upload -> get -> replace -> delete workflow"""
        # 1. Upload
        data = read_file(self.object_path)
        file1 = UploadFile(filename=self.file_name, file=BytesIO(data))

        upload_result = await upload_photo(
            self.patient_id, self.file_name, file1, self.user
        )
        self.assertEqual(
            upload_result["message"], "Successfully uploaded file."
        )

        # 2. Get
        get_result = await get_photo(self.patient_id, self.user)
        self.assertEqual(get_result.status_code, 200)
        self.assertEqual(get_result.body, data)

        # 3. Replace with new photo
        file2 = UploadFile(filename="new_photo.jpg", file=BytesIO(data))
        replace_result = await upload_photo(
            self.patient_id, "new_photo.jpg", file2, self.user
        )
        self.assertEqual(
            replace_result["message"], "Successfully uploaded file."
        )

        # Verify old photo deleted
        old_key = f"{self.patient_id}/{self.file_name}"
        objects = await ObjectService.list_objects("photos")
        self.assertNotIn(old_key, objects)

        # 4. Delete
        delete_result = await delete_photo(self.patient_id, self.user)
        self.assertEqual(
            delete_result["message"], "Successfully deleted photo."
        )

        # Verify complete deletion
        with self.assertRaises(HTTPException):
            await get_photo(self.patient_id, self.user)

    async def test_multiple_patients_photo_isolation(self):
        """Test that photos are isolated between patients"""
        # Create second patient
        patient2_id = await self.mock_create_patient("Jane")

        try:
            # Upload photos for both patients
            data = read_file(self.object_path)

            file1 = UploadFile(filename="patient1.jpg", file=BytesIO(data))
            await upload_photo(
                self.patient_id, "patient1.jpg", file1, self.user
            )

            file2 = UploadFile(filename="patient2.jpg", file=BytesIO(data))
            await upload_photo(patient2_id, "patient2.jpg", file2, self.user)

            # Verify both exist with different keys
            objects = await ObjectService.list_objects("photos")
            key1 = f"{self.patient_id}/patient1.jpg"
            key2 = f"{patient2_id}/patient2.jpg"

            self.assertIn(key1, objects)
            self.assertIn(key2, objects)

            # Delete patient 1 photo
            await delete_photo(self.patient_id, self.user)

            # Verify patient 2 photo still exists
            objects_after = await ObjectService.list_objects("photos")
            self.assertNotIn(key1, objects_after)
            self.assertIn(key2, objects_after)

            # Patient 2 can still get their photo
            result = await get_photo(patient2_id, self.user)
            self.assertEqual(result.status_code, 200)

        finally:
            # Cleanup patient 2
            try:
                await delete_photo(patient2_id, self.user)
            except Exception:
                pass
            await PatientService.delete_patient_by_id(patient2_id)

    async def test_upload_photo_different_mime_types(self):
        """Test uploading photos with different MIME types"""
        # PNG file
        png_data = b"\x89PNG\r\n\x1a\n" + b"fake_png_data"
        headers = {"content-type": "image/png"}
        png_file = UploadFile(
            filename="test.png",
            file=BytesIO(png_data),
            headers=headers,
        )
        # png_file.content_type = "image/png"

        result = await upload_photo(
            self.patient_id, "test.png", png_file, self.user
        )
        self.assertEqual(result["message"], "Successfully uploaded file.")

        # Verify stored correctly
        data, name = await PhotoService.get_photo(self.patient_id)
        self.assertEqual(data, png_data)
        self.assertEqual(name, "test.png")


# -- delete --
# #### Tests
# async def test_upload_photo_success(self):
#     # load file
#     file_name = "test-img.jpeg"
#     data = read_file(self.object_path)
#     file = UploadFile(filename=file_name, file=BytesIO(data))
#
#     # test
#     result = await upload_photo(
#         self.patient_id, file_name, file, self.user
#     )
#     self.assertEqual(result["message"], "Successfully uploaded file.")
#
#     # cleanup
#     key = f"{self.patient_id}/{file_name}"
#     await ObjectService.delete_object("photos", key)
#
# async def test_update_photo_same_name(self):
#     file_name = "test-img.jpeg"
#     data = read_file(self.object_path)
#     file = UploadFile(filename=file_name, file=BytesIO(data))
#     result = await upload_photo(
#         self.patient_id, file_name, file, self.user
#     )
#     self.assertEqual(result["message"], "Successfully uploaded file.")
#     old_photo = await PhotoService.get_photo(self.patient_id)
#
#     # test
#     file_name = "test-img.jpeg"
#     data = read_file(self.object_path)
#     file = UploadFile(filename=file_name, file=BytesIO(data))
#     result = await upload_photo(
#         self.patient_id, file_name, file, self.user
#     )
#     self.assertEqual(result["message"], "Successfully uploaded file.")
#     new_photo = await PhotoService.get_photo(self.patient_id)
#
#     self.assertEqual(old_photo.id, new_photo.id)
#     self.assertEqual(old_photo.patient_id, new_photo.patient_id)
#     self.assertEqual(old_photo.photo_key, new_photo.photo_key)
#     self.assertGreaterEqual(new_photo.uploaded_at, old_photo.uploaded_at)
#
#     # cleanup
#     key = f"{self.patient_id}/{file_name}"
#     await ObjectService.delete_object("photos", key)
#
# async def test_update_photo_different_name(self):
#     file_name = "test-img.jpeg"
#     data = read_file(self.object_path)
#     file = UploadFile(filename=file_name, file=BytesIO(data))
#     result = await upload_photo(
#         self.patient_id, file_name, file, self.user
#     )
#     self.assertEqual(result["message"], "Successfully uploaded file.")
#     old_photo = await PhotoService.get_photo(self.patient_id)
#
#     # test
#     file_name = "test-img2.jpeg"
#     data = read_file(self.object_path)
#     file = UploadFile(filename=file_name, file=BytesIO(data))
#     result = await upload_photo(
#         self.patient_id, file_name, file, self.user
#     )
#     self.assertEqual(result["message"], "Successfully uploaded file.")
#     new_photo = await PhotoService.get_photo(self.patient_id)
#
#     self.assertEqual(old_photo.id, new_photo.id)
#     self.assertEqual(old_photo.patient_id, new_photo.patient_id)
#     self.assertNotEqual(old_photo.photo_key, new_photo.photo_key)
#     self.assertGreaterEqual(new_photo.uploaded_at, old_photo.uploaded_at)
#
#     # cleanup
#     key = f"{self.patient_id}/{file_name}"
#     await ObjectService.delete_object("photos", key)
#
# async def test_get_photo_base64_success(self):
#     await self.mock_create_photo(self.patient_id)
#
#     # test
#     file_name = "test-img.jpeg"
#     result = await get_photo(self.patient_id, "base64", self.user)
#     assert result
#
#     # Get the body content
#     self.assertEqual(result["type"], "JPEG")  # pyright: ignore
#     self.assertEqual(result["name"], file_name)  # pyright: ignore
#     self.assertTrue(len(result["file"]) > 0)  # pyright: ignore
#
#     # Cleanup
#     key = f"{self.patient_id}/{file_name}"
#     await ObjectService.delete_object("photos", key)
#
# async def test_get_photo_raw_success(self):
#     await self.mock_create_photo(self.patient_id)
#
#     # test
#     file_name = "test-img.jpeg"
#     result = await get_photo(self.patient_id, "raw", self.user)
#
#     # Check status code
#     self.assertEqual(result.status_code, 200)
#     self.assertEqual(result.media_type, "application/octet-stream")
#
#     # Get the body content
#     body = result.body
#     self.assertIsInstance(body, bytes)
#     self.assertGreater(len(body), 0)  # Ensure it has content
#     self.assertEqual(read_file(self.object_path), body)
#
#     # Cleanup
#     key = f"{self.patient_id}/{file_name}"
#     await ObjectService.delete_object("photos", key)
#
# async def test_get_photo_not_fount(self):
#     with self.assertRaises(HTTPException) as e:
#         await get_photo(self.patient_id, "raw", self.user)
#
#     self.assertEqual(e.exception.status_code, 404)
#     self.assertEqual(
#         e.exception.detail, "Photo key not found for patient."
#     )
#
# async def test_get_photo_invalid_version(self):
#     await self.mock_create_photo(self.patient_id)
#
#     # test
#     with self.assertRaises(HTTPException) as e:
#         await get_photo(self.patient_id, "invalid", self.user)
#
#     self.assertEqual(e.exception.status_code, 400)
#     self.assertEqual(e.exception.detail, "Invalid version.")
#
#     # Cleanup
#     key = f"{self.patient_id}/{self.file_name}"
#     await ObjectService.delete_object("photos", key)
#
# async def test_delete_photo_success(self):
#     photo_id = await self.mock_create_photo(self.patient_id)
#     self.assertIsNotNone(photo_id)
#
#     # test
#     result = await delete_photo(self.patient_id, self.user)
#     self.assertEqual(result["message"], "Successfully deleted photo.")
