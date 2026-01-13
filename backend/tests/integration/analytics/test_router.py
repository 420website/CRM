# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportAttributeAccessIssue=none
import pandas as pd
from io import BytesIO
import asyncio
from decimal import Decimal
import mimetypes
import re
import uuid
import pyotp
import os
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, Response, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from app.analytics.rag import RagService
from app.analytics.schema import LegacyData
from app.analytics.services import LegacyDataService
from app.authentication.schemas import LoginRequest, MFAVerifiactionCode, RegisterRequest
from app.authentication.services import UserService
from app.database import database, minio_client, redis_client
from app.dependencies import get_current_user, get_user_pending_mfa
from app.objects.schemas import AttachmentCreate
from app.objects.services import AttachmentService, ObjectService
from app.registration.schemas import (
    ActivityCreate,
    AssessmentCreate,
    DispensingCreate,
    InteractionCreate,
    MedicationCreate,
    NoteCreate,
    PatientCreate,
)
from app.registration.services import (
    ActivityService,
    AssessmentService,
    DispensingService,
    InteractionService,
    MedicationService,
    NoteService,
    PatientService,
)
from app.database import mongo_client
from app.config import settings
from datetime import date, datetime
import datetime as dt
from app.authentication.router import (
    login,
    register,
    setup_authenticator_mfa,
    verify_authenticator_mfa,
    verify_email,
)
from app.analytics.router import upload_legacy_data, get_legacy_data_summary, clear_legacy_data_summary
from app.analytics.utils import read_legacy_data_file

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

async def upload_legacy(user_id):
    file = read_csv("tests/integration/analytics/test_data.csv","test_data.csv")
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
    bucket = "testing"
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

    await ObjectService.upload_object(bucket=bucket, key=key, data=file)
    await AttachmentService.upload_attachment(patient_id, metadata)

    
email = "test4@example.com"
password = "securepassword123"

user_create = RegisterRequest(email=email, password=password)
login_request = LoginRequest(email=email, password=password)

@patch("app.authentication.services.EmailService", new_callable=MagicMock)
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


class TestAnalyticsRouter(IsolatedAsyncioTestCase):
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

    async def test_upload_legacy_data_success(self):
        """Test successful upload of legacy data CSV file"""
        file = read_csv(
            "tests/integration/analytics/test_data.csv",
            "test_data.csv"
        )
        
        response = await upload_legacy_data(file=file, user=self.user)
        
        # Verify response structure
        self.assertIsNotNone(response.message)
        self.assertIn("Successfully uploaded", response.message)
        self.assertGreater(response.records_count, 0)
        self.assertIsNotNone(response.preview)
        self.assertIsNotNone(response.upload_id)
        self.assertLessEqual(len(response.preview), 5)
        
        # Verify data was stored
        summary = await LegacyDataService.get_legacy_data_summary(self.user.id)
        self.assertIsNotNone(summary)

    async def test_upload_legacy_data_no_filename(self):
        """Test upload fails when file has no filename"""
        file_bytes = read_file("tests/integration/analytics/test_data.csv")

        file = UploadFile(
            filename=None,  # No filename
            file=BytesIO(file_bytes),
        )
        
        with self.assertRaises(Exception) as context:
            await upload_legacy_data(file=file, user=self.user)
        
        self.assertIn("Please provide file", str(context.exception))

    async def test_upload_legacy_data_invalid_file_type(self):
        """Test upload fails with invalid file type"""
        # Create a mock text file
        file_content = b"This is not a CSV or Excel file"
        file = UploadFile(
            filename="test.txt",
            file=BytesIO(file_content),
        )
        
        with self.assertRaises(Exception) as context:
            await upload_legacy_data(file=file, user=self.user)
        
        self.assertIn("Excel (.xlsx, .xls) or CSV (.csv)", str(context.exception))

    async def test_upload_legacy_data_missing_columns(self):
        """Test upload fails when required columns are missing"""
        # Create CSV with missing columns
        df = pd.DataFrame({
            "PatientID": [1, 2],
            "DOB": ["1990-01-01", "1985-05-15"],
            # Missing many required columns
        })
        
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        file = UploadFile(
            filename="incomplete.csv",
            file=csv_buffer,
        )
        
        with self.assertRaises(Exception) as context:
            await upload_legacy_data(file=file, user=self.user)
        
        self.assertIn("Columns not as expected", str(context.exception))

    async def test_upload_legacy_data_empty_file(self):
        """Test upload fails with empty CSV file"""
        # Create empty DataFrame with correct columns
        expected_columns = [
            "PatientID", "DOB", "Gender", "Address", "City", "Province",
            "PostalCode", "Phone", "HealthCard", "Disposition", "RegDate",
            "ReferralSite", "InteractionType", "Amount"
        ]
        df = pd.DataFrame(columns=expected_columns)
        
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        file = UploadFile(
            filename="empty.csv",
            file=csv_buffer,
        )
        
        with self.assertRaises(Exception) as context:
            await upload_legacy_data(file=file, user=self.user)
        
        self.assertIn("File is empty", str(context.exception))

    async def test_get_legacy_data_summary_success(self):
        """Test retrieving legacy data summary successfully"""
        # First upload some data
        await upload_legacy(self.user.id)
        
        # Get summary
        result = await get_legacy_data_summary(user=self.user)

        # Verify summary contains expected data
        self.assertIsNotNone(result)
        self.assertEqual(result.total_records, 5)
        # self.assertIsNotNone(result.upload_date)

    async def test_get_legacy_data_summary_no_data(self):
        """Test getting summary when no data exists"""
        # Ensure no data exists
        await LegacyDataService.delete_all_legacy_data(self.user.id)
        
        # This might return empty result or raise exception depending on implementation
        with self.assertRaises(HTTPException) as err:
            await get_legacy_data_summary(user=self.user)

        self.assertIn("No legacy data found", str(err.exception))
        
    async def test_get_legacy_data_summary_error_handling(self):
        """Test error handling in get_legacy_data_summary"""
        # Mock service to raise exception
        with patch.object(
            LegacyDataService,
            'get_legacy_data_summary',
            side_effect=Exception("Database error")
        ):
            with self.assertRaises(Exception) as context:
                await get_legacy_data_summary(user=self.user)

            self.assertIn("Failed to get summary data", str(context.exception))

    async def test_clear_legacy_data_summary_success(self):
        """Test clearing legacy data successfully"""
        # First upload some data
        await upload_legacy(self.user.id)
        
        # Verify data exists
        summary_before = await LegacyDataService.get_legacy_data_summary(
            self.user.id
        )
        self.assertIsNotNone(summary_before)
        
        # Clear the data
        result = await clear_legacy_data_summary(user=self.user)
        
        # Verify deletion was successful
        self.assertIsNotNone(result)
        
        # Verify data is gone
        with self.assertRaises(HTTPException) as err:
            await get_legacy_data_summary(user=self.user)

        self.assertIn("No legacy data found", str(err.exception))


    async def test_clear_legacy_data_summary_clears_rag_chat(self):
        """Test that clearing legacy data also clears RAG chat"""
        # Upload data first
        await upload_legacy(self.user.id)
        
        # Mock RagService.clear_chat to verify it's called
        with patch.object(RagService, 'clear_chat') as mock_clear_chat:
            await clear_legacy_data_summary(user=self.user)
            
            # Verify clear_chat was called with correct user_id
            mock_clear_chat.assert_called_once_with(self.user.id)

    async def test_clear_legacy_data_summary_error_handling(self):
        """Test error handling in clear_legacy_data_summary"""
        # Mock service to raise exception
        with patch.object(
            LegacyDataService,
            'delete_all_legacy_data',
            side_effect=Exception("Delete failed")
        ):
            with self.assertRaises(Exception) as context:
                await clear_legacy_data_summary(user=self.user)
            
            self.assertIn("Failed to delete summary data", str(context.exception))

    async def test_clear_legacy_data_summary_when_no_data(self):
        """Test clearing when no data exists (should not fail)"""
        # Ensure no data exists
        await LegacyDataService.delete_all_legacy_data(self.user.id)
        
        # Should complete without error
        result = await clear_legacy_data_summary(user=self.user)
        self.assertIsNotNone(result)

    async def test_upload_then_get_summary(self):
        """Integration test: upload data then retrieve summary"""
        # Upload data
        file = read_csv(
            "tests/integration/analytics/test_data.csv",
            "test_data.csv"
        )
        await upload_legacy_data(file=file, user=self.user)
        
        # Get summary
        summary = await get_legacy_data_summary(user=self.user)
        
        # Verify consistency between upload and summary
        self.assertIsNotNone(summary)

    async def test_upload_multiple_files_overwrites(self):
        """Test that uploading a new file handles previous data correctly"""
        # Upload first file
        file1 = read_csv(
            "tests/integration/analytics/test_data.csv",
            "test_data_1.csv"
        )
        response1 = await upload_legacy_data(file=file1, user=self.user)
        upload_id_1 = response1.upload_id
        
        # Upload second file
        file2 = read_csv(
            "tests/integration/analytics/test_data.csv",
            "test_data_2.csv"
        )
        response2 = await upload_legacy_data(file=file2, user=self.user)
        upload_id_2 = response2.upload_id
        
        # Verify different upload IDs
        self.assertNotEqual(upload_id_1, upload_id_2)
        
        # Verify summary reflects latest upload
        summary = await get_legacy_data_summary(user=self.user)
        self.assertIsNotNone(summary)

    async def test_upload_excel_file(self):
        """Test uploading an Excel file (.xlsx)"""
        # Create a simple Excel file
        df = pd.DataFrame({
            "PatientID": [1, 2, 3],
            "DOB": ["1990-01-01", "1985-05-15", "1992-08-20"],
            "Gender": ["M", "F", "M"],
            "Address": ["123 Main", "456 Oak", "789 Pine"],
            "City": ["Toronto", "Ottawa", "Montreal"],
            "Province": ["ON", "ON", "QC"],
            "PostalCode": ["M1A1A1", "K1A1A1", "H1A1A1"],
            "Phone": ["1111111111", "2222222222", "3333333333"],
            "HealthCard": ["1234567890", "0987654321", "1122334455"],
            "Disposition": ["Active", "Inactive", "Active"],
            "RegDate": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "ReferralSite": ["Site A", "Site B", "Site C"],
            "InteractionType": ["Type1", "Type2", "Type1"],
            "Amount": [100.00, 200.00, 150.00],
        })
        
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)
        
        file = UploadFile(
            filename="test_data.xlsx",
            file=excel_buffer,
        )
        
        response = await upload_legacy_data(file=file, user=self.user)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.records_count, 3)
        self.assertIn("Successfully uploaded", response.message)

    async def test_rag_chat_cleared_on_upload(self):
        """Test that RAG chat is cleared when uploading new data"""
        with patch.object(RagService, 'clear_chat') as mock_clear_chat:
            file = read_csv(
                "tests/integration/analytics/test_data.csv",
                "test_data.csv"
            )
            await upload_legacy_data(file, self.user)
            
            # Verify clear_chat was called during upload
            mock_clear_chat.assert_called_once_with(self.user.id)
