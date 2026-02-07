# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportAttributeAccessIssue=none
from io import BytesIO
import json
import asyncio
from decimal import Decimal
import mimetypes
import re
import uuid
import pyotp
import os
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, patch
import time
from fastapi import Response, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from app.core.analytics.rag import RagService
from app.core.analytics.schema import LegacyData
from app.core.analytics.services import LegacyDataService
from app.core.authentication.schemas import (
    LoginRequest,
    MFAVerifiactionCode,
    RegisterRequest,
)
from app.core.authentication.services import UserService
from app.common.storage.postgres import database
from app.common.storage.redis import redis_client
from app.common.storage.minio import minio_client
from app.common.dependencies import get_current_user, get_user_pending_mfa
from app.core.objects.schemas import AttachmentCreate
from app.core.objects.object_queries import ObjectService
from app.core.objects.attachment_service import AttachmentService
from app.core.registration.schemas import (
    ActivityCreate,
    AssessmentCreate,
    DispensingCreate,
    InteractionCreate,
    MedicationCreate,
    NoteCreate,
    PatientCreate,
)
from app.core.registration.services import (
    ActivityService,
    AssessmentService,
    DispensingService,
    InteractionService,
    MedicationService,
    NoteService,
    PatientService,
)
from app.common.storage.mongodb import mongo_client
from app.common.config import settings
from datetime import date, datetime
import datetime as dt
from app.core.authentication.router import (
    login,
    register,
    setup_authenticator_mfa,
    verify_authenticator_mfa,
    verify_email,
)
from app.core.analytics.utils import read_legacy_data_file


def read_file(path: str) -> bytes:
    with open(path, "rb") as file:
        file_bytes = file.read()
        return file_bytes


def read_csv(path, filename):
    file_bytes = read_file(path)
    return UploadFile(
        filename=filename,
        file=BytesIO(file_bytes),
        # content_type="text/csv",
    )


async def upload_legacy_data(user_id):
    file = read_csv(
        "tests/integration/analytics/test_data.csv", "test_data.csv"
    )
    df = await read_legacy_data_file(file)

    data = LegacyData(
        user_id=user_id,
        upload_id=str(uuid.uuid4()),
        filename=file.filename,
        upload_date=datetime.now(),
        records_count=len(df),
        columns=list(df.columns),
        data=df.to_dict("records"),
    )
    await LegacyDataService.insert_legacy_data(data)


async def upload_attachment(patient_id: int, file_name: str, path: str):
    # bucket = "testing"
    key = f"{patient_id}/{file_name}"

    file = read_file(path)

    mime_type, _ = mimetypes.guess_type(path)
    if mime_type is None:
        mime_type = "application/octet-stream"  # default for unknown types

    # Get document type (extension)
    document_type = os.path.splitext(path)[1].lstrip(".")
    if not document_type:
        document_type = "pdf"

    # # Create AttachmentCreate from form fields
    metadata = AttachmentCreate(
        file_name=file_name,
        file_key=key,
        file_size=file.__sizeof__(),
        mime_type=mime_type,
        document_type=document_type,
    )

    await AttachmentService.upload_attachment(patient_id, file, metadata)


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


class TestRagService(IsolatedAsyncioTestCase):
    async def _cleanup_test_data(self):
        """Helper method to clean up test data"""
        # Clean up test patients
        test_names = [
            ("John", "Doe"),
            ("Bobby", "Doe"),
            ("Tim", "Tom"),
            ("Jane", "Smith"),
        ]
        for first, last in test_names:
            try:
                await PatientService.delete_patient(first, last)
            except Exception:
                pass  # Ignore if patient doesn't exist

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
        asyncio.get_event_loop().set_debug(False)

    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await minio_client.connect()
        await database.connect()
        await redis_client.connect()
        await mongo_client.connect()

        # Clear out old users
        await UserService.delete_user(email, password)
        self.user = await self.get_validated_user()

        self.bucket = "testing"
        try:
            await ObjectService.create_bucket(self.bucket)
        except Exception:
            pass

        await self._cleanup_test_data()

        self.patient = PatientCreate(
            # Required fields
            first_name="John",
            last_name="Doe",
            dob=date(1985, 6, 15),
            # Optional demographic fields
            age=38,
            gender="Male",
            aka="Johnny",
            address="123 Main Street",
            unit_number="Apt 4B",
            city="Toronto",
            province="Ontario",
            postal_code="M5V 3A8",
            phone1="416-555-0123",
            phone2="647-555-0456",
            email="john.doe@email.com",
            # Health info
            health_card="0000000000",
            health_card_version="AB",
            coverage_type="OHIP",
            disposition="Follow-up required",
            physician="Dr. Smith",
            # Consent / communication
            patient_consent="Verbal consent given",
            leave_message=True,
            voicemail=True,
            text=False,
            preferred_time="Morning 9-11 AM",
            # Test results
            rna_available="Yes",
            rna_result="Not Detected",
            rna_sample_date=date(2023, 12, 1),
            # Referral / registration
            referral_site="Downtown Health Clinic",
            referral_person="Nurse Johnson",
            reg_date=date(2023, 11, 28),
            # Notes / misc
            special_attention="Patient has hearing difficulties",
            instructions="Call before 8 PM",
            selected_template="Standard HIV Template",
            summary_template="Brief Summary",
            # test_type="HIV Screening",
        )

        await PatientService.create_patient(self.patient)
        patients = await PatientService.get_patients()
        # print(patients)
        self.patient_id = patients[0].id

        self.assessment_data = AssessmentCreate(
            type="HIV",
            date=date(2025, 10, 10),
            result="Negative",
            tester="Tester A",
            data={"hiv_type": "Rapid"},
        )
        await AssessmentService.create_assessment(
            self.patient_id, self.assessment_data
        )

        # A valid note to use
        self.note_data = NoteCreate(
            # patient_id=self.patient_id,
            note_text="Initial consultation notes",
            note_date=date(2024, 1, 1),
            template_type="testing",
        )
        await NoteService.create_note(self.patient_id, self.note_data)

        self.interaction_data = InteractionCreate(
            description="Initial payment",
            date=date(2024, 1, 1),
            referral_id="REF123",
            amount=Decimal("100.00"),
            payment_type="Cash",
            issued="Admin",
        )
        await InteractionService.create_interaction(
            self.patient_id, self.interaction_data
        )

        self.medication_data = MedicationCreate(
            medication="Aspirin",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 10),
            outcome="Recovered",
        )
        await MedicationService.create_medication(
            self.patient_id, self.medication_data
        )

        self.dispensing_data = DispensingCreate(
            medication="Aspirin",
            rx="RX123",
            quantity=30,
            lot="LOT456",
            product_type="Tablet",
            expiry_date=date(2025, 1, 1),
        )
        await DispensingService.create_dispensing(
            self.patient_id, self.dispensing_data
        )

        self.activity_data = ActivityCreate(
            date=date(2024, 1, 1),
            time=dt.time(9, 0),
            name="Delivery",
            description="Initial activity",
        )
        await ActivityService.create_activity(
            self.patient_id, self.activity_data
        )

    async def asyncTearDown(self) -> None:
        await ObjectService.delete_objects(self.bucket, "")
        await ObjectService.delete_bucket(self.bucket)
        await self._cleanup_test_data()
        await LegacyDataService.delete_all_legacy_data(self.user.id)

        await mongo_client.disconnect()
        await redis_client.disconnect()
        await minio_client.disconnect()
        await database.disconnect()

    # @skip
    async def test_update_chat_new(self):
        check = await RagService.get_chat(self.user.id)
        self.assertFalse(check)

        # Updated
        await RagService.update_chat(self.user.id, "user", "User message1")

        # Validate
        result = await RagService.get_chat(self.user.id)
        self.assertTrue(len(result) == 1)
        self.assertEqual(result[0]["role"], "user")
        self.assertEqual(result[0]["content"], "User message1")

    async def test_update_chat_existing(self):
        await RagService.update_chat(self.user.id, "user", "User message1")

        # Add new message
        await RagService.update_chat(
            self.user.id, "assistant", "Assistant message1"
        )

        # Validate
        result = await RagService.get_chat(self.user.id)
        self.assertTrue(len(result) == 2)
        self.assertEqual(result[0]["role"], "user")
        self.assertEqual(result[0]["content"], "User message1")
        self.assertEqual(result[1]["role"], "assistant")
        self.assertEqual(result[1]["content"], "Assistant message1")

    async def test_tty_clears_chat(self):
        settings.chat_history_ttl = 1
        await RagService.update_chat(self.user.id, "user", "User message1")

        # Check
        time.sleep(3)
        result = await RagService.get_chat(self.user.id)
        self.assertTrue(len(result) == 0)

        settings.chat_history_ttl = 20 * 60

    async def test_max_length_enforced(self):
        settings.max_chat_length = 2
        await RagService.update_chat(self.user.id, "user", "User message1")
        await RagService.update_chat(
            self.user.id, "assistant", "Assistant message1"
        )
        await RagService.update_chat(self.user.id, "user", "User message2")

        # Check
        result = await RagService.get_chat(self.user.id)
        self.assertTrue(len(result) == 2)
        self.assertEqual(result[0]["role"], "assistant")
        self.assertEqual(result[0]["content"], "Assistant message1")
        self.assertEqual(result[1]["role"], "user")
        self.assertEqual(result[1]["content"], "User message2")

        settings.max_chat_length = 20

    async def test_get_chat_no_chat(self):
        result = await RagService.get_chat(self.user.id)
        self.assertEqual(result, [])

    async def test_clear_chat(self):
        await RagService.update_chat(self.user.id, "user", "User message1")
        result = await RagService.get_chat(self.user.id)
        self.assertEqual(len(result), 1)

        # Test
        await RagService.clear_chat(self.user.id)

        # Check
        result = await RagService.get_chat(self.user.id)
        self.assertEqual(result, [])

    async def test_handle_query_postgres(self):
        query = "SELECT * FROM patients"
        result = await RagService.handle_query_postgres(query)

        # Check
        self.assertEqual(type(result), str)

        parsed = json.loads(result)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["id"], self.patient_id)

    async def test_handle_query_postgres_non_select(self):
        query = "DELETE * FROM patients"
        result = await RagService.handle_query_postgres(query)

        parsed = json.loads(result)
        self.assertIn("Only SELECT", parsed["error"])

    async def test_handle_query_postgres_invalid_query(self):
        query = "not event sql"
        result = await RagService.handle_query_postgres(query)

        parsed = json.loads(result)
        self.assertIn("Only SELECT", parsed["error"])

    async def test_handle_query_postgres_error_on_query(self):
        query = "SELECT * FROM not_table"
        result = await RagService.handle_query_postgres(query)

        parsed = json.loads(result)
        self.assertIn('relation "not_table" does not exist', parsed["error"])

    async def test_handle_query_mongodb(self):
        file = read_csv(
            "tests/integration/analytics/test_data.csv", "test_data.csv"
        )
        df = await read_legacy_data_file(file)

        data = LegacyData(
            user_id=self.user.id,
            upload_id=str(uuid.uuid4()),
            filename=file.filename,
            upload_date=datetime.now(),
            records_count=len(df),
            columns=list(df.columns),
            data=df.to_dict("records"),
        )
        await LegacyDataService.insert_legacy_data(data)

        # Test
        pipeline = [
            {"$unwind": "$data"},  # Required to access nested fields
            {"$match": {"data.City": "Toronto"}},  # Example filter
            {
                "$project": {  # Only return these fields
                    "_id": 0,
                    "PatientID": "$data.PatientID",
                    "Phone": "$data.Phone",
                    "DOB": "$data.DOB",
                    "Amount": "$data.Amount",
                }
            },
            {
                "$group": {
                    "_id": "$data.City",
                    "total_patients": {"$sum": 1},
                    "total_amount": {"$sum": "$data.Amount"},
                }
            },
        ]

        result = await RagService.handle_query_mongodb(self.user.id, pipeline)
        self.assertEqual(type(result), str)

        data = json.loads(result)
        self.assertEqual(data[0]["total_patients"], 1)

    async def test_handle_query_mongodb_no_records(self):
        # Test
        pipeline = [
            {"$unwind": "$data"},  # Required to access nested fields
            {"$match": {"data.City": "Toronto"}},  # Example filter
            {
                "$project": {  # Only return these fields
                    "_id": 0,
                    "PatientID": "$data.PatientID",
                    "Phone": "$data.Phone",
                    "DOB": "$data.DOB",
                    "Amount": "$data.Amount",
                }
            },
            {
                "$group": {
                    "_id": "$data.City",
                    "total_patients": {"$sum": 1},
                    "total_amount": {"$sum": "$data.Amount"},
                }
            },
        ]

        result = await RagService.handle_query_mongodb(self.user.id, pipeline)

        data = json.loads(result)
        self.assertIn("No legacy data found", data["error"])

    async def test_handle_query_mongodb_invalid(self):
        file = read_csv(
            "tests/integration/analytics/test_data.csv", "test_data.csv"
        )
        df = await read_legacy_data_file(file)

        data = LegacyData(
            user_id=self.user.id,
            upload_id=str(uuid.uuid4()),
            filename=file.filename,
            upload_date=datetime.now(),
            records_count=len(df),
            columns=list(df.columns),
            data=df.to_dict("records"),
        )
        await LegacyDataService.insert_legacy_data(data)

        # Test
        pipeline = {"data.City": "Toronto"}
        result = await RagService.handle_query_mongodb(self.user.id, pipeline)

        data = json.loads(result)
        self.assertIn(
            'can only concatenate list (not "dict") to list', data["error"]
        )

    # TODO: Write the tests for prompt claude  with claude mocked
