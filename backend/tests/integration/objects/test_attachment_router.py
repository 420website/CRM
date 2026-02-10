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
from app.core.registration.router import create_patient
from app.core.registration.schemas import PatientCreate
from app.core.objects.object_queries import ObjectService
from app.core.objects.attachment_service import AttachmentService
from app.core.registration.services import PatientService
from app.core.authentication.router import (
    login,
    register,
    setup_authenticator_mfa,
    verify_authenticator_mfa,
    verify_email,
)
from app.core.objects.router import (
    delete_attachment,
    get_attachment,
    list_attachment_objects,
    upload_attachment,
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


class TestPatientAttachmentsRouter(IsolatedAsyncioTestCase):
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
        # Clear out old users
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

    async def mock_create_attachment(self, patient_id: int) -> str:
        """Helper to create an attachment for a patient and return file_key"""
        data = read_file(self.object_path)
        file = UploadFile(filename=self.file_name, file=BytesIO(data))
        await upload_attachment(
            patient_id,
            file=file,
            file_name=self.file_name,
            file_size=len(data),
            mime_type="application/pdf",
            document_type="Consultation Report",
            _=self.user,
        )
        # Get the created attachment to return its file_key
        attachments = await AttachmentService.get_patient_attachments(
            patient_id
        )

        return attachments[0].file_key

    async def asyncSetUp(self) -> None:
        await database.connect()
        await minio_client.connect()
        asyncio.get_event_loop().set_debug(False)

        self.file_name = "test-pdf.pdf"
        self.object_path = "tests/integration/objects/docs/test-pdf.pdf"

        # Create test patient
        self.patient_id = await self.mock_create_patient("Timothy")

    async def asyncTearDown(self):
        # Clean up all attachments for this patient
        attachments = await AttachmentService.get_patient_attachments(
            self.patient_id
        )
        for attachment in attachments:
            try:
                await AttachmentService.delete_attachment(attachment.file_key)
            except Exception:
                pass

        await PatientService.delete_patient_by_id(self.patient_id)
        await minio_client.disconnect()
        await database.disconnect()

    #### UPLOAD TESTS
    async def test_upload_attachment_success(self):
        data = read_file(self.object_path)
        file = UploadFile(filename=self.file_name, file=BytesIO(data))

        # Test
        result = await upload_attachment(
            patient_id=self.patient_id,
            file=file,
            file_name=self.file_name,
            file_size=len(data),
            mime_type="application/pdf",
            document_type="Consultation Report",
            _=self.user,
        )

        # Validate response
        self.assertEqual(
            result["message"],
            "Attachment uploaded successfully.",
        )

        # Validate database record
        attachments = await AttachmentService.get_patient_attachments(
            self.patient_id
        )
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0].file_name, self.file_name)

        # Validate MinIO object
        objects = await ObjectService.list_objects("attachments")
        self.assertIn(attachments[0].file_key, objects)

    async def test_upload_attachment_empty_file(self):
        # Create empty file
        empty_data = b""
        file = UploadFile(filename="empty.pdf", file=BytesIO(empty_data))

        # Test - should still succeed (validation should happen at form level)
        result = await upload_attachment(
            patient_id=self.patient_id,
            file=file,
            file_name="empty.pdf",
            file_size=0,
            mime_type="application/pdf",
            document_type="Consultation Report",
            _=self.user,
        )

        self.assertEqual(
            result["message"],
            "Attachment uploaded successfully.",
        )

    async def test_upload_attachment_large_file(self):
        # Create a larger test file (1MB)
        large_data = b"x" * (1024 * 1024)
        file = UploadFile(filename="large.pdf", file=BytesIO(large_data))

        # Test
        result = await upload_attachment(
            patient_id=self.patient_id,
            file=file,
            file_name="large.pdf",
            file_size=len(large_data),
            mime_type="application/pdf",
            document_type="Consultation Report",
            _=self.user,
        )

        self.assertEqual(
            result["message"],
            "Attachment uploaded successfully.",
        )

        # Validate the file was stored correctly
        attachments = await AttachmentService.get_patient_attachments(
            self.patient_id
        )
        self.assertEqual(attachments[0].file_size, len(large_data))

    #### LIST TESTS
    async def test_list_attachments_empty(self):
        # Test
        result = await list_attachment_objects(self.patient_id, self.user)

        # Validate
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    async def test_list_attachments_single(self):
        file_key = await self.mock_create_attachment(self.patient_id)
        self.assertIsNotNone(file_key)

        # Test
        result = await list_attachment_objects(self.patient_id, self.user)

        # Validate
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].file_name, self.file_name)
        self.assertEqual(result[0].file_key, file_key)

    async def test_list_attachments_multiple(self):
        # Create first attachment
        await self.mock_create_attachment(self.patient_id)

        # Create second attachment with different name
        data = read_file(self.object_path)
        file2 = UploadFile(filename="second.pdf", file=BytesIO(data))
        await upload_attachment(
            patient_id=self.patient_id,
            file=file2,
            file_name="second.pdf",
            file_size=len(data),
            mime_type="application/pdf",
            document_type="Lab Report",
            _=self.user,
        )

        # Test
        result = await list_attachment_objects(self.patient_id, self.user)

        # Validate
        self.assertEqual(len(result), 2)
        file_names = [att.file_name for att in result]
        self.assertIn(self.file_name, file_names)
        self.assertIn("second.pdf", file_names)

    #### GET TESTS
    async def test_get_attachment_success(self):
        file_key = await self.mock_create_attachment(self.patient_id)
        self.assertIsNotNone(file_key)

        # Test
        result = await get_attachment(file_key, self.user)

        # Validate response
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.media_type, "application/pdf")

        # Validate content
        self.assertIsInstance(result.body, bytes)
        self.assertGreater(len(result.body), 0)
        self.assertEqual(read_file(self.object_path), result.body)

    async def test_get_attachment_not_found(self):
        # Test with non-existent key
        with self.assertRaises(HTTPException) as context:
            await get_attachment(
                "nonexistent/key/file.pdf",
                self.user,
            )

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(
            context.exception.detail,
            "Attachment not found",
        )

    async def test_get_attachment_different_mime_types(self):
        # Test with image file
        image_data = b"fake_image_data"
        file = UploadFile(filename="test.jpg", file=BytesIO(image_data))

        await upload_attachment(
            patient_id=self.patient_id,
            file=file,
            file_name="test.jpg",
            file_size=len(image_data),
            mime_type="image/jpeg",
            document_type="Photo ID",
            _=self.user,
        )

        # Get attachment
        attachments = await AttachmentService.get_patient_attachments(
            self.patient_id
        )
        jpg_attachment = next(
            (att for att in attachments if att.file_name == "test.jpg"), None
        )
        self.assertIsNotNone(jpg_attachment)

        # Test
        result = await get_attachment(jpg_attachment.file_key, self.user)

        # Validate
        self.assertEqual(result.media_type, "image/jpeg")
        self.assertEqual(result.body, image_data)

    #### DELETE TESTS
    async def test_delete_attachment_success(self):
        file_key = await self.mock_create_attachment(self.patient_id)
        self.assertIsNotNone(file_key)

        # Verify it exists before deletion
        attachments_before = await AttachmentService.get_patient_attachments(
            self.patient_id
        )
        self.assertEqual(len(attachments_before), 1)

        # Test
        result = await delete_attachment(file_key, self.user)

        # Validate response
        self.assertEqual(result["message"], "Successfully deleted attachment.")

        # Validate database deletion
        attachments_after = await AttachmentService.get_patient_attachments(
            self.patient_id
        )
        self.assertEqual(len(attachments_after), 0)

        # Validate MinIO deletion
        objects = await ObjectService.list_objects("attachments")
        self.assertNotIn(file_key, objects)

    async def test_delete_attachment_not_found(self):
        # Test with non-existent key
        with self.assertRaises(HTTPException) as context:
            await delete_attachment(
                "nonexistent/key/file.pdf",
                self.user,
            )

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(
            context.exception.detail,
            "Attachment not found",
        )

    async def test_delete_attachment_idempotent(self):
        file_key = await self.mock_create_attachment(self.patient_id)
        self.assertIsNotNone(file_key)

        # Delete first time
        result1 = await delete_attachment(file_key, self.user)
        self.assertEqual(
            result1["message"], "Successfully deleted attachment."
        )

        # Try to delete again - should raise 404
        with self.assertRaises(HTTPException) as context:
            await delete_attachment(file_key, self.user)

        self.assertEqual(context.exception.status_code, 404)

    #### INTEGRATION TESTS
    async def test_full_attachment_workflow(self):
        """Test complete upload -> list -> get -> delete workflow"""
        data = read_file(self.object_path)

        # 1. Upload
        file = UploadFile(filename=self.file_name, file=BytesIO(data))
        upload_result = await upload_attachment(
            patient_id=self.patient_id,
            file=file,
            file_name=self.file_name,
            file_size=len(data),
            mime_type="application/pdf",
            document_type="Consultation Report",
            _=self.user,
        )
        self.assertEqual(
            upload_result["message"],
            "Attachment uploaded successfully.",
        )

        # 2. List
        attachments = await list_attachment_objects(self.patient_id, self.user)
        self.assertEqual(len(attachments), 1)
        file_key = attachments[0].file_key

        # 3. Get
        get_result = await get_attachment(file_key, self.user)
        self.assertEqual(get_result.status_code, 200)
        self.assertEqual(get_result.body, data)

        # 4. Delete
        delete_result = await delete_attachment(file_key, self.user)
        self.assertEqual(
            delete_result["message"],
            "Successfully deleted attachment.",
        )

        # 5. Verify deletion
        final_attachments = await list_attachment_objects(
            self.patient_id, self.user
        )
        self.assertEqual(len(final_attachments), 0)

    async def test_multiple_patients_isolation(self):
        """Verify attachments are properly isolated between patients"""
        # Create second patient
        patient2_id = await self.mock_create_patient("SecondPatient")

        try:
            # Upload to first patient
            await self.mock_create_attachment(self.patient_id)

            # Upload to second patient
            data = read_file(self.object_path)
            file2 = UploadFile(filename="patient2.pdf", file=BytesIO(data))
            await upload_attachment(
                patient_id=patient2_id,
                file=file2,
                file_name="patient2.pdf",
                file_size=len(data),
                mime_type="application/pdf",
                document_type="Consultation Report",
                _=self.user,
            )

            # Verify patient 1 only sees their attachment
            patient1_attachments = await list_attachment_objects(
                self.patient_id, self.user
            )
            self.assertEqual(len(patient1_attachments), 1)
            self.assertEqual(patient1_attachments[0].file_name, self.file_name)

            # Verify patient 2 only sees their attachment
            patient2_attachments = await list_attachment_objects(
                patient2_id, self.user
            )
            self.assertEqual(len(patient2_attachments), 1)
            self.assertEqual(patient2_attachments[0].file_name, "patient2.pdf")

        finally:
            # Cleanup patient 2
            await PatientService.delete_patient_by_id(patient2_id)


# -- old ---
# email = "test497@example.com"
# password = "securepassword123"
#
#
# class TestPatientAttachmentsRouter(IsolatedAsyncioTestCase):
#     @classmethod
#     async def get_validated_user(cls):
#         token = await mock_register()
#         await verify_email(token)
#         response = await login(login_request)
#
#         credentials = HTTPAuthorizationCredentials(
#             scheme="Bearer",
#             credentials=response.access_token,
#         )
#
#         user = await get_user_pending_mfa(credentials=credentials)
#         response = await setup_authenticator_mfa(user)
#         totp = pyotp.TOTP(response.secret)
#         code = totp.now()
#
#         user = await get_user_pending_mfa(credentials=credentials)
#         response = Response()
#         result = await verify_authenticator_mfa(
#             MFAVerifiactionCode(code=code), response, user
#         )
#
#         credentials = HTTPAuthorizationCredentials(
#             scheme="Bearer",
#             credentials=result.access_token,
#         )
#
#         user = await get_current_user(credentials=credentials)
#         return user
#
#     @classmethod
#     async def asyncSetUpClass(cls):
#         await database.connect()
#
#         # Clear out old users
#         await UserService.delete_user(email, password)
#         cls.user = await cls.get_validated_user()
#
#         await database.disconnect()
#
#     @classmethod
#     async def asyncTearDownClass(cls):
#         await database.connect()
#         await UserService.delete_user(email, password)
#         await database.disconnect()
#
#     @property
#     def user(self):
#         return self.__class__.user
#
#     async def mock_create_patient(self, name: str):
#         """Helper to create a test patient using class user"""
#         patient_data = PatientCreate(
#             first_name=name,
#             last_name="Doe",
#             dob=date(1990, 1, 1),
#             age=33,
#             gender="Male",
#             email="jim.doe@example.com",
#             phone1="416-555-0123",
#             status="pending",
#             health_card="0000000000",
#             health_card_version="AB",
#             disposition="Active",
#             referral_site="Toronto",
#             province="Ontario",
#         )
#
#         result = await create_patient(patient_data, self.user)
#         return result["patient_id"]
#
#     async def mock_create_attachment(self, patient_id):
#         """Helper to create an attachment for a patient"""
#         data = read_file(self.object_path)
#         file = UploadFile(filename=self.file_name, file=BytesIO(data))
#
#         await upload_attachment(
#             patient_id,
#             file=file,
#             file_name=self.file_name,
#             file_size=len(data),
#             mime_type="application/pdf",
#             document_type="Consultation Report",
#             _=self.user,
#         )
#
#         # Get the created attachment to return its ID
#         attachments = await AttachmentService.get_patient_attachments(
#             patient_id
#         )
#         return attachments[0].id if attachments else None
#
#     async def asyncSetUp(self) -> None:
#         await database.connect()
#         await minio_client.connect()
#         asyncio.get_event_loop().set_debug(False)
#
#         self.file_name = "test-pdf.pdf"
#         self.object_path = "tests/integration/objects/docs/test-pdf.pdf"
#         self.patient_data = PatientCreate(
#             first_name="Timothy",
#             last_name="Doe",
#             dob=date(1990, 1, 1),
#             age=33,
#             gender="Male",
#             email="jim.doe@example.com",
#             phone1="416-555-0123",
#             status="pending",
#             health_card="0000000000",
#             health_card_version="AB",
#             disposition="Active",
#             referral_site="Toronto",
#             province="Ontario",
#         )
#
#         self.patient_id = await self.mock_create_patient("Timothy")
#
#         # Attachment test data
#         self.attachment_data = AttachmentCreate(
#             file_name=f"{self.file_name}",
#             file_key=f"{self.patient_id}/{self.file_name}",
#             file_size=1024,
#             mime_type="application/pdf",
#             document_type="Consultation Report",
#         )
#
#         self.key = f"{self.patient_id}/{self.file_name}"
#
#     async def asyncTearDown(self):
#         await PatientService.delete_patient_by_id(self.patient_id)
#         await minio_client.disconnect()
#         await database.disconnect()
#
#     async def test_upload_attachment_success(self):
#         data = read_file(self.object_path)
#         file = UploadFile(filename=self.file_name, file=BytesIO(data))
#
#         # test
#         result = await upload_attachment(
#             patient_id=self.patient_id,
#             file=file,
#             file_name=self.file_name,
#             file_size=len(data),
#             mime_type="application/pdf",
#             document_type="Consultation Report",
#             _=self.user,
#         )
#
#         self.assertEqual(
#             result["message"],
#             "Attachment uploaded successfully.",
#         )
#
#         # Cleanup
#         await ObjectService.delete_object("attachments", self.key)
#
#     async def test_list_attachments(self):
#         id = await self.mock_create_attachment(self.patient_id)
#         self.assertIsNotNone(id)
#
#         # test
#         result = await list_attachment_objects(self.patient_id)
#         self.assertEqual(len(result), 1)
#
#         # validate
#         await ObjectService.delete_object("attachments", self.key)
#
#     async def test_list_attachments_none(self):
#         # test
#         result = await list_attachment_objects(self.patient_id)
#         self.assertEqual(len(result), 0)
#
#     async def test_get_attachments_by_patient_raw_success(self):
#         await self.mock_create_attachment(self.patient_id)
#
#         # test
#         result = await get_attachment(
#             self.patient_id,
#             self.file_name,
#             "raw",
#             self.user,
#         )
#
#         # Check status code
#         self.assertEqual(result.status_code, 200)
#         self.assertEqual(result.media_type, "application/pdf")
#
#         # Get the body content
#         body = result.body
#         self.assertIsInstance(body, bytes)
#         self.assertGreater(len(body), 0)  # Ensure it has content
#         self.assertEqual(read_file(self.object_path), body)
#
#         # Cleanup
#         await ObjectService.delete_object("attachments", self.key)
#
#     async def test_get_attachments_by_patient_not_found(self):
#         # test
#         with self.assertRaises(HTTPException) as e:
#             await get_attachment(
#                 self.patient_id,
#                 self.file_name,
#                 "raw",
#                 self.user,
#             )
#         self.assertEqual(e.exception.status_code, 404)
#         self.assertEqual(
#             e.exception.detail, "Attachment not found for patient."
#         )
#
#     async def test_get_attachments_invalid_version(self):
#         await self.mock_create_attachment(self.patient_id)
#
#         # test
#         with self.assertRaises(HTTPException) as e:
#             await get_attachment(
#                 self.patient_id,
#                 self.file_name,
#                 "other",
#                 self.user,
#             )
#         self.assertEqual(e.exception.status_code, 400)
#         self.assertEqual(
#             e.exception.detail, "Invalid version. Must be 'raw' or 'base64'."
#         )
#
#         # clean up
#         await ObjectService.delete_object("attachments", self.key)
#
#     async def test_delete_attachment_success(self):
#         id = await self.mock_create_attachment(self.patient_id)
#         self.assertIsNotNone(id)
#
#         # test
#         result = await delete_attachment(self.patient_id, self.file_name)
#         self.assertEqual(result["message"], "Successfully deleted attachment.")
