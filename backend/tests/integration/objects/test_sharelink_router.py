# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportOperatorIssue=none, reportAttributeAccessIssue=none
import asyncio
from datetime import datetime, timedelta
import datetime as dt
from io import BytesIO
from unittest import IsolatedAsyncioTestCase
from datetime import date
from fastapi import HTTPException, Response, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from app.core.authentication.services import UserService
from app.common.storage.postgres import database
from app.common.storage.minio import minio_client
from app.common.dependencies import get_current_user, get_user_pending_mfa
import pyotp
from app.core.objects.attachment_service import AttachmentService
from app.core.objects.router import upload_attachment
from app.core.objects.object_queries import ObjectService
from app.core.registration.router import create_patient
from app.core.registration.schemas import PatientCreate
from app.core.registration.services import PatientService
from app.common.config import settings
from app.testing.router import register_user
from app.core.authentication.router import (
    login,
    setup_authenticator_mfa,
    verify_authenticator_mfa,
)
from app.core.authentication.schemas import (
    LoginRequest,
    MFAVerifiactionCode,
    RegisterRequest,
)
from app.core.objects.router import (
    AttachmentId,
    access_share_link,
    create_share_link,
    decode_jwt,
    get_share_link_metadata,
)


def read_file(path: str) -> bytes:
    with open(path, "rb") as file:
        file_bytes = file.read()
        return file_bytes


email = "test978@example.com"
password = "securepassword123"

user_create = RegisterRequest(email=email, password=password)
login_request = LoginRequest(email=email, password=password)


class TestShareLinkRouter(IsolatedAsyncioTestCase):
    @classmethod
    async def get_validated_user(cls):
        await register_user(user_create)
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

    async def mock_create_attachment(self, patient_id: int) -> tuple[int, str]:
        """Helper to create an attachment for a patient.
        Returns tuple of (attachment_id, file_key)"""
        file_name = "test-pdf.pdf"
        data = read_file(self.object_path)
        file = UploadFile(filename=file_name, file=BytesIO(data))

        await upload_attachment(
            patient_id,
            file=file,
            file_name=file_name,
            file_size=len(data),
            mime_type="application/pdf",
            document_type="Consultation Report",
            _=self.user,
        )

        # Get the created attachment to return its ID and file_key
        attachments = await AttachmentService.get_patient_attachments(
            patient_id
        )
        # if attachments:
        return attachments[0].id, attachments[0].file_key
        # return None, None

    @classmethod
    async def asyncSetUpClass(cls):
        await database.connect()
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

    async def asyncSetUp(self) -> None:
        await database.connect()
        await minio_client.connect()
        asyncio.get_event_loop().set_debug(False)

        self.object_path = "tests/integration/objects/docs/test-pdf.pdf"
        self.patient_data = PatientCreate(
            first_name="Jimothy",
            last_name="Doe",
            dob=date(1990, 1, 1),
            age=33,
            gender="Male",
            email="jim.doe@example.com",
            phone1="416-555-0123",
            status="pending",
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
        )
        result = await create_patient(self.patient_data, self.user)
        self.patient_id = result["patient_id"]

    async def asyncTearDown(self):
        # Clean up all attachments for this patient
        attachments = await AttachmentService.get_patient_attachments(
            self.patient_id
        )
        for attachment in attachments:
            try:
                await ObjectService.delete_object(
                    "attachments", attachment.file_key
                )
            except Exception:
                pass

        await PatientService.delete_patient_by_id(self.patient_id)
        await minio_client.disconnect()
        await database.disconnect()

    #### CREATE SHARE LINK TESTS
    async def test_create_share_link_success(self):
        """Test creating a share link for an attachment"""
        attachment_id, file_key = await self.mock_create_attachment(
            self.patient_id
        )
        self.assertIsNotNone(attachment_id)
        self.assertIsNotNone(file_key)

        # Test
        result = await create_share_link(
            AttachmentId(attachment_id=attachment_id), self.user
        )

        # Validate response structure
        self.assertIn("share_url", result)
        self.assertTrue(result["share_url"].startswith(settings.app_url))

        # Extract and decode token
        token = result["share_url"].split("token=")[1]
        decoded_token = decode_jwt(token)

        # Validate token payload
        assert decoded_token
        self.assertIsNotNone(decoded_token)
        self.assertEqual(decoded_token["file_key"], file_key)
        self.assertEqual(decoded_token["file_name"], "test-pdf.pdf")
        self.assertEqual(decoded_token["mime_type"], "application/pdf")

        # Validate token expiry
        self.assertGreater(
            decoded_token["exp"],
            datetime.now(dt.timezone.utc).timestamp(),
        )
        self.assertLess(
            decoded_token["iat"],
            datetime.now(dt.timezone.utc).timestamp(),
        )

    async def test_create_share_link_attachment_not_found(self):
        """Test creating share link for non-existent attachment"""
        non_existent_id = 999999

        with self.assertRaises(HTTPException) as context:
            await create_share_link(
                AttachmentId(attachment_id=non_existent_id), self.user
            )

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Attachment not found.")

    async def test_create_share_link_url_format(self):
        """Test that share link URL is correctly formatted"""
        attachment_id, _ = await self.mock_create_attachment(self.patient_id)

        result = await create_share_link(
            AttachmentId(attachment_id=attachment_id), self.user
        )

        # Validate URL format
        expected_prefix = f"{settings.app_url}/crm/share-link?token="
        self.assertTrue(result["share_url"].startswith(expected_prefix))

        # Ensure token is present
        token_part = result["share_url"].split("token=")[1]
        self.assertGreater(
            len(token_part), 20
        )  # JWT should be reasonably long

    #### GET SHARE LINK METADATA TESTS
    async def test_get_share_link_metadata_success(self):
        """Test retrieving metadata from a valid share link token"""
        attachment_id, _ = await self.mock_create_attachment(self.patient_id)

        # Create share link
        result = await create_share_link(
            AttachmentId(attachment_id=attachment_id), self.user
        )
        token = result["share_url"].split("token=")[1]

        # Test
        metadata = await get_share_link_metadata(token)

        # Validate
        self.assertEqual(metadata["file_name"], "test-pdf.pdf")
        self.assertEqual(metadata["mime_type"], "application/pdf")

    async def test_get_share_link_metadata_expired_token(self):
        """Test metadata retrieval with expired token"""
        # Create expired token
        expiry = datetime.now(dt.timezone.utc) - timedelta(minutes=5)
        payload = {
            "file_key": "123/456/test.pdf",
            "file_name": "test.pdf",
            "mime_type": "application/pdf",
            "exp": int(expiry.timestamp()),
            "iat": int(datetime.now(dt.timezone.utc).timestamp()),
        }
        token = jwt.encode(
            payload,
            settings.jwt_access_secret,
            algorithm=settings.jwt_algorithm,
        )

        # Test
        with self.assertRaises(HTTPException) as context:
            await get_share_link_metadata(token)

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Url has expired.")

    async def test_get_share_link_metadata_invalid_token(self):
        """Test metadata retrieval with invalid/malformed token"""
        invalid_token = "invalid.token.here"

        with self.assertRaises(HTTPException) as context:
            await get_share_link_metadata(invalid_token)

        self.assertEqual(context.exception.status_code, 401)

    #### ACCESS SHARE LINK TESTS
    async def test_access_share_link_success(self):
        """Test accessing attachment via share link"""
        attachment_id, _ = await self.mock_create_attachment(self.patient_id)

        # Create share link
        result = await create_share_link(
            AttachmentId(attachment_id=attachment_id), self.user
        )
        token = result["share_url"].split("token=")[1]

        # Test - access the attachment
        response = await access_share_link(token)

        # Validate response
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.body, bytes)
        self.assertGreater(len(response.body), 0)

        # Validate content matches original file
        original_data = read_file(self.object_path)
        self.assertEqual(response.body, original_data)

    async def test_access_share_link_expired_token(self):
        """Test accessing attachment with expired token"""
        # Create expired token with realistic file_key format
        expiry = datetime.now(dt.timezone.utc) - timedelta(minutes=5)
        payload = {
            "file_key": f"{self.patient_id}/123/test.pdf",
            "file_name": "test.pdf",
            "mime_type": "application/pdf",
            "exp": int(expiry.timestamp()),
            "iat": int(datetime.now(dt.timezone.utc).timestamp()),
        }
        token = jwt.encode(
            payload,
            settings.jwt_access_secret,
            algorithm=settings.jwt_algorithm,
        )

        with self.assertRaises(HTTPException) as context:
            await access_share_link(token)

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Url has expired.")

    async def test_access_share_link_deleted_attachment(self):
        """Test accessing share link after attachment is deleted"""
        attachment_id, file_key = await self.mock_create_attachment(
            self.patient_id
        )

        # Create share link
        result = await create_share_link(
            AttachmentId(attachment_id=attachment_id), self.user
        )
        token = result["share_url"].split("token=")[1]

        # Delete the attachment from MinIO
        await ObjectService.delete_object("attachments", file_key)

        # Test - should fail to find attachment
        with self.assertRaises(HTTPException):
            await access_share_link(token)

        # self.assertEqual(context.exception.status_code, 404)
        # self.assertEqual(context.exception.detail, "Attachment not found.")

    async def test_access_share_link_invalid_token(self):
        """Test accessing attachment with malformed token"""
        invalid_token = "totally.invalid.token"

        with self.assertRaises(HTTPException) as context:
            await access_share_link(invalid_token)

        self.assertEqual(context.exception.status_code, 401)

    #### INTEGRATION TESTS
    async def test_share_link_full_workflow(self):
        """Test complete share link workflow: create -> get metadata -> access"""
        # 1. Create attachment
        attachment_id, _ = await self.mock_create_attachment(self.patient_id)
        self.assertIsNotNone(attachment_id)

        # 2. Create share link
        share_result = await create_share_link(
            AttachmentId(attachment_id=attachment_id), self.user
        )
        token = share_result["share_url"].split("token=")[1]

        # 3. Get metadata
        metadata = await get_share_link_metadata(token)
        self.assertEqual(metadata["file_name"], "test-pdf.pdf")
        self.assertEqual(metadata["mime_type"], "application/pdf")

        # 4. Access attachment
        response = await access_share_link(token)
        self.assertEqual(response.status_code, 200)

        # 5. Verify content
        original_data = read_file(self.object_path)
        self.assertEqual(response.body, original_data)

    async def test_share_link_token_contains_correct_file_key(self):
        """Verify token contains the complete file_key, not reconstructed path"""
        attachment_id, file_key = await self.mock_create_attachment(
            self.patient_id
        )

        # Create share link
        result = await create_share_link(
            AttachmentId(attachment_id=attachment_id), self.user
        )
        token = result["share_url"].split("token=")[1]
        decoded = decode_jwt(token)

        # Verify the token contains the actual file_key from database
        assert decoded
        self.assertEqual(decoded["file_key"], file_key)

        # Verify file_key has correct format: {patient_id}/{attachment_id}/{file_name}
        parts = file_key.split("/")
        self.assertEqual(len(parts), 3)
        self.assertEqual(parts[0], str(self.patient_id))
        self.assertTrue(parts[1].isdigit())  # attachment_id
        self.assertEqual(parts[2], "test-pdf.pdf")

    async def test_share_link_multiple_attachments_isolation(self):
        """Verify share links work correctly for multiple attachments"""
        # Create two attachments
        id1, key1 = await self.mock_create_attachment(self.patient_id)

        # Create second attachment with different name
        data = read_file(self.object_path)
        file2 = UploadFile(filename="second.pdf", file=BytesIO(data))
        await upload_attachment(
            self.patient_id,
            file=file2,
            file_name="second.pdf",
            file_size=len(data),
            mime_type="application/pdf",
            document_type="Lab Report",
            _=self.user,
        )
        attachments = await AttachmentService.get_patient_attachments(
            self.patient_id
        )
        id2 = next(
            (a.id for a in attachments if a.file_name == "second.pdf"), None
        )
        key2 = next(
            (a.file_key for a in attachments if a.file_name == "second.pdf"),
            None,
        )

        # Create share links for both
        link1 = await create_share_link(
            AttachmentId(attachment_id=id1), self.user
        )
        link2 = await create_share_link(
            AttachmentId(attachment_id=id2), self.user
        )

        token1 = link1["share_url"].split("token=")[1]
        token2 = link2["share_url"].split("token=")[1]

        # Verify tokens are different
        self.assertNotEqual(token1, token2)

        # Verify each token accesses correct file
        metadata1 = await get_share_link_metadata(token1)
        metadata2 = await get_share_link_metadata(token2)

        self.assertEqual(metadata1["file_name"], "test-pdf.pdf")
        self.assertEqual(metadata2["file_name"], "second.pdf")

        # Verify decoded file_keys are correct
        decoded1 = decode_jwt(token1)
        decoded2 = decode_jwt(token2)

        assert decoded1
        assert decoded2
        self.assertEqual(decoded1["file_key"], key1)
        self.assertEqual(decoded2["file_key"], key2)


# -- delete --
#
# class TestShareLinkRouter(IsolatedAsyncioTestCase):
#     @classmethod
#     async def get_validated_user(cls):
#         await register_user(user_create)
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
#     async def mock_create_attachment(self, patient_id):
#         """Helper to create an attachment for a patient"""
#         file_name = "test_document.pdf"
#
#         data = read_file(self.object_path)
#         file = UploadFile(filename=file_name, file=BytesIO(data))
#         await upload_attachment(
#             patient_id,
#             file=file,
#             file_name="test-pdf.pdf",
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
#     @classmethod
#     async def asyncSetUpClass(cls):
#         await database.connect()
#
#         await UserService.delete_user(email, password)
#         cls.user = await cls.get_validated_user()
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
#     async def asyncSetUp(self) -> None:
#         await database.connect()
#         await minio_client.connect()
#         asyncio.get_event_loop().set_debug(False)
#
#         self.object_path = "tests/integration/objects/docs/test-pdf.pdf"
#         self.patient_data = PatientCreate(
#             first_name="Jimothy",
#             last_name="Doe",
#             dob=date(1990, 1, 1),
#             age=33,
#             gender="Male",
#             email="jim.doe@example.com",
#             phone1="416-555-0123",
#             status="pending",
#             health_card="1234567890",
#             health_card_version="AB",
#             disposition="Active",
#             referral_site="Toronto",
#             province="Ontario",
#         )
#         result = await create_patient(self.patient_data, self.user)
#         self.patient_id = result["patient_id"]
#
#     async def asyncTearDown(self):
#         key = f"{self.patient_id}/test-pdf.pdf"
#         await ObjectService.delete_object("attachments", key)
#         await PatientService.delete_patient_by_id(self.patient_id)
#         await PatientService.delete_patient_by_id(self.patient_id)
#         await minio_client.disconnect()
#         await database.disconnect()
#
#     # create patient
#     async def test_share_link_success(self):
#         """Helper to create an attachment for a patient"""
#         id = await self.mock_create_attachment(self.patient_id)
#
#         # test
#         result = await create_share_link(AttachmentId(attachment_id=id))
#         token = result["share_url"].split("?")[1]
#         token = token.split("=")[1]
#         decode_token = decode_jwt(token)
#         assert decode_token
#
#         # validate
#         # self.assertEqual(decode_token["attachment_id"], attachment_id)
#         self.assertGreater(
#             decode_token["exp"],
#             datetime.now(dt.timezone.utc).timestamp(),
#         )
#         self.assertLess(
#             decode_token["iat"],
#             datetime.now(dt.timezone.utc).timestamp(),
#         )
#
#     async def test_share_link_no_attachment(self):
#         """Helper to create an attachment for a patient"""
#         attachment_id = 109876
#
#         # test
#         with self.assertRaises(HTTPException) as cm:
#             await create_share_link(AttachmentId(attachment_id=attachment_id))
#
#         self.assertEqual(cm.exception.status_code, 404)
#         self.assertEqual(cm.exception.detail, "Attachment not found.")
#
#     async def test_access_share_link_metadata_successful(self):
#         """Helper to create an attachment for a patient"""
#         id = await self.mock_create_attachment(self.patient_id)
#
#         result = await create_share_link(AttachmentId(attachment_id=id))
#         token = result["share_url"].split("?")[1]
#         token = token.split("=")[1]
#
#         # test
#         response = await get_share_link_metadata(token)
#
#         # validate
#         self.assertEqual("test-pdf.pdf", response["file_name"])
#         self.assertEqual("application/pdf", response["mime_type"])
#
#     async def test_access_share_link_successful(self):
#         """Helper to create an attachment for a patient"""
#         id = await self.mock_create_attachment(self.patient_id)
#
#         result = await create_share_link(AttachmentId(attachment_id=id))
#         token = result["share_url"].split("?")[1]
#         token = token.split("=")[1]
#
#         # test
#         result = await access_share_link(token)
#
#         # Check status code
#         self.assertEqual(result.status_code, 200)
#
#         # Get the body content
#         body = result.body
#         self.assertIsInstance(body, bytes)
#         self.assertGreater(len(body), 0)  # Ensure it has content
#         self.assertEqual(read_file(self.object_path), body)
#
#     async def test_access_share_link_invalid_jwt(self):
#         expiry = datetime.now(dt.timezone.utc) - timedelta(minutes=5)
#         payload = {
#             "attachment_id": 1,
#             "exp": int(expiry.timestamp()),
#             "iat": int(datetime.now(dt.timezone.utc).timestamp()),
#         }
#
#         token = jwt.encode(
#             payload,
#             settings.jwt_access_secret,
#             algorithm=settings.jwt_algorithm,
#         )
#
#         with self.assertRaises(HTTPException) as cm:
#             await access_share_link(token)
#
#         self.assertEqual(cm.exception.status_code, 401)
#         self.assertEqual(cm.exception.detail, "Url has expired.")
