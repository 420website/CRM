# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportAttributeAccessIssue=none
import asyncio
from decimal import Decimal
import mimetypes
import os
from unittest import IsolatedAsyncioTestCase, skip
from app.analytics.prompts import internal_system_message
from app.analytics.rag import RagService
from app.analytics.schema import ClaudeChatRequest
from app.database import database, minio_client, redis_client
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
from datetime import date, datetime
import datetime as dt
from zoneinfo import ZoneInfo


def read_file(path: str) -> bytes:
    with open(path, "rb") as file:
        file_bytes = file.read()
        return file_bytes


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
    async def asyncSetUpClass(cls):
        asyncio.get_event_loop().set_debug(False)

    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await minio_client.connect()
        await database.connect()
        await redis_client.connect()

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

        await redis_client.disconnect()
        await minio_client.disconnect()
        await database.disconnect()

    @skip
    async def test_prompt_midday(self):
        # Request
        tz = ZoneInfo("America/Toronto")
        time = datetime(2025, 2, 1, 12, 0, 0, tzinfo=tz)
        iso_string = time.isoformat()

        request = ClaudeChatRequest(
            legacy_data=False,
            message="How many documents were uploaded under attachments today ?",
            datetime=iso_string,
        )

        # Test
        schema = await RagService.get_schema()
        query = await RagService.generate_query(schema, request)

        # validate
        expected_query = """
        SELECT *
         FROM attachments a
         WHERE a.uploaded_at >= '2025-02-01 05:00:00+00:00'
         AND a.uploaded_at < '2025-02-02 05:00:00+00:00'
        """

        self.assertEqual(
            " ".join(query.split()), " ".join(expected_query.split())
        )

    @skip
    async def test_prompt_morning(self):
        # Request
        tz = ZoneInfo("America/Toronto")
        time = datetime(2025, 2, 1, 1, 0, 0, tzinfo=tz)
        iso_string = time.isoformat()

        request = ClaudeChatRequest(
            legacy_data=False,
            message="How many documents were uploaded under attachments today ?",
            datetime=iso_string,
        )

        # # Test
        schema = await RagService.get_schema()
        query = await RagService.generate_query(schema, request)

        # validate
        expected_query = """
        SELECT *
         FROM attachments a
         WHERE a.uploaded_at >= '2025-02-01 05:00:00+00:00'
         AND a.uploaded_at < '2025-02-02 05:00:00+00:00'
        """

        self.assertEqual(
            " ".join(query.split()), " ".join(expected_query.split())
        )

    @skip
    async def test_prompt_night(self):
        # Request
        tz = ZoneInfo("America/Toronto")
        time = datetime(2025, 2, 1, 23, 0, 0, tzinfo=tz)
        iso_string = time.isoformat()

        request = ClaudeChatRequest(
            legacy_data=False,
            message="How many documents were uploaded under attachments today ?",
            datetime=iso_string,
        )

        # Test
        schema = await RagService.get_schema()
        query = await RagService.generate_query(schema, request)

        # validate
        expected_query = """
        SELECT *
         FROM attachments a
         WHERE a.uploaded_at >= '2025-02-01 05:00:00+00:00'
         AND a.uploaded_at < '2025-02-02 05:00:00+00:00'
        """

        self.assertEqual(
            " ".join(query.split()), " ".join(expected_query.split())
        )

    @skip
    async def test_prompt_by_date(self):
        # Request
        tz = ZoneInfo("America/Toronto")
        time = datetime(2025, 2, 1, 23, 0, 0, tzinfo=tz)
        iso_string = time.isoformat()

        request = ClaudeChatRequest(
            legacy_data=False,
            message="How many documents were uploaded under attachments nov 26th 2025 ?",
            datetime=iso_string,
        )

        # Test
        schema = await RagService.get_schema()
        query = await RagService.generate_query(schema, request)

        # validate
        expected_query = """
        SELECT *
         FROM attachments a
         WHERE a.uploaded_at >= '2025-11-26 05:00:00+00:00'
         AND a.uploaded_at < '2025-11-27 05:00:00+00:00'
        """

        self.assertEqual(
            " ".join(query.split()), " ".join(expected_query.split())
        )

    @skip
    async def test_prompt_by_week(self):
        # Request
        tz = ZoneInfo("America/Toronto")
        time = datetime(2025, 11, 29, 23, 0, 0, tzinfo=tz)
        iso_string = time.isoformat()

        request = ClaudeChatRequest(
            legacy_data=False,
            message="How many documents were uploaded under attachments this week ?",
            datetime=iso_string,
        )

        # Test
        schema = await RagService.get_schema()
        query = await RagService.generate_query(schema, request)

        # validate
        expected_query = """
        SELECT *
         FROM attachments a
         WHERE a.uploaded_at >= '2025-11-24 05:00:00+00:00'
         AND a.uploaded_at < '2025-12-01 05:00:00+00:00'
        """

        self.assertEqual(
            " ".join(query.split()), " ".join(expected_query.split())
        )

    @skip
    async def test_prompt_by_month(self):
        # Request
        tz = ZoneInfo("America/Toronto")
        time = datetime(2025, 11, 29, 23, 0, 0, tzinfo=tz)
        iso_string = time.isoformat()

        request = ClaudeChatRequest(
            legacy_data=False,
            message="How many documents were uploaded under attachments this month ?",
            datetime=iso_string,
        )

        # Test
        schema = await RagService.get_schema()
        query = await RagService.generate_query(schema, request)

        # validate
        expected_query = """
        SELECT *
         FROM attachments a
         WHERE a.uploaded_at >= '2025-11-01 05:00:00+00:00'
         AND a.uploaded_at < '2025-12-01 05:00:00+00:00'
        """

        self.assertEqual(
            " ".join(query.split()), " ".join(expected_query.split())
        )

    @skip
    async def test_prompt_by_year(self):
        # Request
        tz = ZoneInfo("America/Toronto")
        time = datetime(2025, 11, 29, 23, 0, 0, tzinfo=tz)
        iso_string = time.isoformat()

        request = ClaudeChatRequest(
            legacy_data=False,
            message="How many documents were uploaded under attachments this year ?",
            datetime=iso_string,
        )

        # Test
        schema = await RagService.get_schema()
        query = await RagService.generate_query(schema, request)

        # validate
        expected_query = """
        SELECT *
         FROM attachments a
         WHERE a.uploaded_at >= '2025-01-01 05:00:00+00:00'
         AND a.uploaded_at < '2026-01-01 05:00:00+00:00'
        """

        self.assertEqual(
            " ".join(query.split()), " ".join(expected_query.split())
        )

    @skip
    async def test_prompt_internal(self):
        tz = ZoneInfo("America/Toronto")
        now_local = datetime.now(tz)
        iso_string_local = now_local.isoformat()

        request = ClaudeChatRequest(
            legacy_data=False,
            message="How many HCV,HIV and bloodwork tests were completed this month?",
            datetime=iso_string_local,
        )

        question = ()
        schema = await RagService.get_schema()
        query = await RagService.generate_query(schema, question)
        context = await RagService.retrieve_context(query)
        system_msg = internal_system_message(context)
        answer = await RagService.prompt_llm(system_msg, question, "14232")
