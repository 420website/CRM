# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportAttributeAccessIssue=none
import asyncio
from decimal import Decimal
from unittest import IsolatedAsyncioTestCase
from app.analytics.prompts import internal_system_message
from app.analytics.rag import RagService
from app.database import database
from app.registration.schemas import (
    ActivityCreate,
    DispensingCreate,
    InteractionCreate,
    MedicationCreate,
    NoteCreate,
    PatientCreate,
    TestCreate,
)
from app.registration.services import (
    ActivityService,
    DispensingService,
    InteractionService,
    MedicationService,
    NoteService,
    PatientService,
    TestService,
)
from datetime import date
import datetime as dt


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

    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)

        await database.connect()
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
            hiv_date=date(2023, 12, 1),
            hiv_result="Negative",
            hiv_tester="Lab Tech A",
            hiv_type="Rapid Test",
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
            test_type="HIV Screening",
        )

        await PatientService.create_patient(self.patient)
        patients = await PatientService.get_patients()
        self.patient_id = patients[0].id

        self.test_data = TestCreate(
            test_type="HIV Screening",
            test_date=date(2025, 10, 10),
            hiv_result="Negative",
            hiv_type="Rapid",
            hiv_tester="Tester A",
            hcv_result=None,
            hcv_tester=None,
            bloodwork_type="CBC",
            bloodwork_circles="2",
            bloodwork_result="Normal",
            bloodwork_date_submitted=date(2025, 10, 10),
            bloodwork_tester="Lab Tech B",
        )
        await TestService.create_test(self.patient_id, self.test_data)

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
            description="Initial activity",
            date=date(2024, 1, 1),
            time=dt.time(9, 0),
        )
        await ActivityService.create_activity(
            self.patient_id, self.activity_data
        )

    async def asyncTearDown(self) -> None:
        await self._cleanup_test_data()
        await database.disconnect()

    # create
    async def test_prompt_internal(self):
        question = (
            "How many HCV,HIV and bloodwork tests were completed this month?"
        )
        schema = await RagService.get_schema()
        query = await RagService.generate_query(schema, question)
        context = await RagService.retrieve_context(query)
        system_msg = internal_system_message(context)
        answer = await RagService.prompt_llm(system_msg, question, "14232")
        # answer = await RagService.prompt_llm()
        print(answer)
