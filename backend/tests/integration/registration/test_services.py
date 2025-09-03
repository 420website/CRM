# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportAttributeAccessIssue=none
import asyncio
from decimal import Decimal
from unittest import IsolatedAsyncioTestCase
from app.database import database
from app.registration.schemas import (
    ActivityCreate,
    ActivityUpdate,
    AttachmentCreate,
    AttachmentUpdate,
    DispensingCreate,
    DispensingUpdate,
    InteractionCreate,
    InteractionUpdate,
    MedicationCreate,
    MedicationUpdate,
    NoteCreate,
    NoteUpdate,
    PatientCreate,
    PatientRead,
    PatientUpdate,
    TestCreate,
    TestUpdate,
)
from app.registration.services import (
    ActivityService,
    AttachmentService,
    DispensingService,
    InteractionService,
    MedicationService,
    NoteService,
    PatientService,
    TestService,
)
from datetime import date
import datetime as dt


class TestPatientService(IsolatedAsyncioTestCase):
    async def _cleanup_test_data(self):
        """Helper method to clean up test data"""
        # Clean up test patients
        test_names = [("John", "Doe"), ("Tim", "Tom"), ("Jane", "Smith")]
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
            health_card="1234567890",
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
            photo="patient_photo_base64_string_here",
        )

        # Minimal PatientCreate instance with only required fields
        self.minimal_patient = PatientCreate(
            first_name="John",
            last_name="Doe",
            dob=date(1990, 3, 22),
        )
        self.minimal_patient2 = PatientCreate(
            first_name="Jane",
            last_name="Smith",
            dob=date(1990, 3, 22),
        )

        # PatientCreate for testing edge cases
        self.edge_case_patient = PatientCreate(
            first_name="María José",
            last_name="García-González",
            dob=date(2000, 1, 1),
            # Testing optional fields with various data types
            age=24,
            gender="Female",
            email="maria.garcia@test-email.com",
            phone1="+1-800-555-9999",
            postal_code="K1A 0A6",  # Canadian postal code format
            leave_message=False,
            voicemail=False,
            text=True,
            hiv_date=date(2024, 1, 15),
            reg_date=date(2024, 1, 10),
        )

    async def asyncTearDown(self) -> None:
        await self._cleanup_test_data()
        await database.disconnect()

    # create
    async def test_create_patient_success(self):
        """Test successful creation of a patient"""
        # Test
        result = await PatientService.create_patient(self.patient)
        self.assertTrue(result)

        # Validate
        patients = await PatientService.get_patients()
        self.assertEqual(patients[0].first_name, self.patient.first_name)

    async def test_create_patient_with_default(self):
        """Test creation of a default patient"""

        # Test
        result = await PatientService.create_patient(self.minimal_patient)
        self.assertTrue(result)

        # Validate
        patients = await PatientService.get_patients()
        self.assertEqual(
            patients[0].first_name, self.minimal_patient.first_name
        )
        self.assertIsNotNone(patients[0].id)

    ### Get
    async def test_get_patient_empty(self):
        """Test getting patients when none exist"""
        patients = await PatientService.get_patients()

        self.assertIsInstance(patients, list)
        self.assertEqual(len(patients), 0)

    async def test_get_patient_with_data(self):
        """Test getting patients when data exists"""
        # Create test patients

        await PatientService.create_patient(self.minimal_patient)
        await PatientService.create_patient(self.minimal_patient2)

        patients = await PatientService.get_patients()

        self.assertIsInstance(patients, list)
        self.assertGreaterEqual(len(patients), 2)

        # Verify our patients are in the results
        patient_names = [p.first_name for p in patients]
        self.assertIn("Jane", patient_names)
        self.assertIn("John", patient_names)

        # Verify patient structure
        for patient in patients:
            self.assertIsInstance(patient, PatientRead)
            self.assertIsInstance(patient.id, int)
            self.assertIsInstance(patient.first_name, str)
            self.assertIsInstance(patient.last_name, str)
            self.assertIsInstance(patient.dob, dt.date)

    #### delete
    async def test_delete_patient_success(self):
        """Test successful deletion of a patient"""
        await PatientService.create_patient(self.minimal_patient)

        # Delete the patient
        result = await PatientService.delete_patient(
            self.minimal_patient.first_name, self.minimal_patient.last_name
        )
        self.assertTrue(result)

        # Verify patient was deleted
        patients = await PatientService.get_patients()
        patient_names = [p.first_name for p in patients]
        self.assertNotIn(self.minimal_patient.first_name, patient_names)

    async def test_delete_patient_not_found(self):
        """Test deletion of non-existent patient"""
        result = await PatientService.delete_patient("other", "name")

        self.assertFalse(result)

    #####  Update
    async def test_update_patient_success(self):
        """Test successful update of a patient"""
        await PatientService.create_patient(self.minimal_patient)

        # Update the patient
        update_data = PatientUpdate(
            first_name="Tim",
            last_name="Tom",
        )
        patients = await PatientService.get_patients()
        result = await PatientService.update_patient(
            patients[0].id,
            update_data,
        )
        self.assertTrue(result)

        # Verify patient was updated
        patients = await PatientService.get_patients()

        self.assertIsNotNone(patients[0])
        self.assertEqual(patients[0].first_name, "Tim")
        self.assertEqual(patients[0].last_name, "Tom")

    async def test_update_patient_partial(self):
        """Test partial update of a patient"""
        await PatientService.create_patient(self.minimal_patient)

        # Partial update - only is_frequent
        update_data = PatientUpdate(
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
        )

        patients = await PatientService.get_patients()
        result = await PatientService.update_patient(
            patients[0].id,
            update_data,
        )
        self.assertTrue(result)

        # Verify only is_frequent was updated
        patients = await PatientService.get_patients()
        self.assertIsNotNone(patients[0])
        self.assertEqual(patients[0].address, "123 Main Street")
        self.assertEqual(patients[0].unit_number, "Apt 4B")

    async def test_update_patient_empty_updates(self):
        """Test update with no actual changes"""
        await PatientService.create_patient(self.minimal_patient)

        # Empty update
        update_data = PatientUpdate()
        result = await PatientService.update_patient(1, update_data)

        self.assertFalse(result)

    async def test_update_patient_not_found(self):
        """Test update of non-existent patient"""
        update_data = PatientUpdate(
            first_name="John",
            last_name="Doe",
            dob=date(1985, 6, 15),
        )

        result = await PatientService.update_patient(1, update_data)

        self.assertFalse(result)


class TestTestsService(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()
        await PatientService.delete_patient("Jim", "Doe")

        # Create a minimal patient for linking tests
        self.minimal_patient = PatientCreate(
            first_name="Jim",
            last_name="Doe",
            dob=date(1990, 3, 22),
        )
        await PatientService.create_patient(self.minimal_patient)
        patients = await PatientService.get_patients()
        self.patient_id = patients[0].id

        # A valid test to use
        self.test_data = TestCreate(
            test_type="HIV Screening",
            test_date=date(2024, 1, 1),
            hiv_result="Negative",
            hiv_type="Rapid",
            hiv_tester="Tester A",
            hcv_result=None,
            hcv_tester=None,
            bloodwork_type="CBC",
            bloodwork_circles="2",
            bloodwork_result="Normal",
            bloodwork_date_submitted=date(2024, 1, 2),
            bloodwork_tester="Lab Tech B",
        )

    async def asyncTearDown(self) -> None:
        await PatientService.delete_patient("Jim", "Doe")
        await database.disconnect()

    #### CREATE
    async def test_create_test_success(self):
        result = await TestService.create_test(self.patient_id, self.test_data)
        self.assertTrue(result)

        tests = await TestService.get_tests()
        self.assertGreaterEqual(len(tests), 1)
        self.assertEqual(tests[0].test_type, "HIV Screening")

    #### GET
    async def test_get_tests_empty(self):
        tests = await TestService.get_tests()
        self.assertIsInstance(tests, list)
        self.assertEqual(len(tests), 0)

    async def test_get_tests_by_patient(self):
        await TestService.create_test(self.patient_id, self.test_data)
        await TestService.create_test(
            self.patient_id,
            TestCreate(
                test_type="Bloodwork",
                test_date=date(2024, 2, 1),
                hiv_result=None,
                hiv_type=None,
                hiv_tester=None,
                hcv_result="Negative",
                hcv_tester="Tester B",
                bloodwork_type="CMP",
                bloodwork_circles="1",
                bloodwork_result="Normal",
                bloodwork_date_submitted=date(2024, 2, 2),
                bloodwork_tester="Lab Tech C",
            ),
        )

        tests = await TestService.get_tests_by_patient(self.patient_id)
        self.assertGreaterEqual(len(tests), 2)
        self.assertEqual(tests[0].test_type, "Bloodwork")  # newest first

    #### UPDATE
    async def test_update_test_success(self):
        await TestService.create_test(self.patient_id, self.test_data)
        tests = await TestService.get_tests()
        test_id = tests[0].id

        update_data = TestUpdate(hiv_result="Positive")
        result = await TestService.update_test(test_id, update_data)
        self.assertTrue(result)

        updated_tests = await TestService.get_tests()
        self.assertEqual(updated_tests[0].hiv_result, "Positive")

    async def test_update_test_empty_updates(self):
        await TestService.create_test(self.patient_id, self.test_data)
        tests = await TestService.get_tests()
        test_id = tests[0].id

        update_data = TestUpdate()
        result = await TestService.update_test(test_id, update_data)
        self.assertFalse(result)

    async def test_update_test_not_found(self):
        update_data = TestUpdate(hiv_result="Positive")
        result = await TestService.update_test(9999, update_data)  # invalid ID
        self.assertFalse(result)

    #### DELETE
    async def test_delete_test_success(self):
        await TestService.create_test(self.patient_id, self.test_data)
        tests = await TestService.get_tests()
        test_id = tests[0].id

        result = await TestService.delete_test_by_id(test_id)
        self.assertTrue(result)

        remaining = await TestService.get_tests()
        self.assertEqual(len(remaining), 0)

    async def test_delete_test_not_found(self):
        result = await TestService.delete_test_by_id(9999)
        self.assertFalse(result)


class TestNotesService(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()

        # Ensure no leftover patients or notes
        await PatientService.delete_patient("Jim", "Doe")

        # Create a minimal patient for linking notes
        self.minimal_patient = PatientCreate(
            first_name="Jim",
            last_name="Doe",
            dob=date(1990, 3, 22),
        )
        await PatientService.create_patient(self.minimal_patient)
        patients = await PatientService.get_patients()
        self.patient_id = patients[0].id

        # A valid note to use
        self.note_data = NoteCreate(
            # patient_id=self.patient_id,
            note_text="Initial consultation notes",
            note_date=date(2024, 1, 1),
            template_type="testing",
        )

    async def asyncTearDown(self) -> None:
        await PatientService.delete_patient("Jim", "Doe")
        await database.disconnect()

    #### CREATE
    async def test_create_note_success(self):
        result = await NoteService.create_note(self.patient_id, self.note_data)
        self.assertTrue(result)

        notes = await NoteService.get_notes()
        self.assertGreaterEqual(len(notes), 1)
        self.assertEqual(notes[0].note_text, "Initial consultation notes")

    #### GET
    async def test_get_notes_empty(self):
        notes = await NoteService.get_notes()
        self.assertIsInstance(notes, list)
        self.assertEqual(len(notes), 0)

    async def test_get_notes_by_patient(self):
        await NoteService.create_note(self.patient_id, self.note_data)
        await NoteService.create_note(
            self.patient_id,
            NoteCreate(
                note_text="Follow-up note",
                note_date=date(2024, 2, 1),
                template_type="testing",
            ),
        )

        notes = await NoteService.get_notes_by_patient(self.patient_id)
        self.assertGreaterEqual(len(notes), 2)
        self.assertEqual(notes[0].note_text, "Follow-up note")  # newest first

    #### UPDATE
    async def test_update_note_success(self):
        await NoteService.create_note(self.patient_id, self.note_data)
        notes = await NoteService.get_notes()
        note_id = notes[0].id

        update_data = NoteUpdate(note_text="Updated consultation note")
        result = await NoteService.update_note(note_id, update_data)
        self.assertTrue(result)

        updated_notes = await NoteService.get_notes()
        self.assertEqual(
            updated_notes[0].note_text, "Updated consultation note"
        )

    async def test_update_note_empty_updates(self):
        await NoteService.create_note(self.patient_id, self.note_data)
        notes = await NoteService.get_notes()
        note_id = notes[0].id

        update_data = NoteUpdate()
        result = await NoteService.update_note(note_id, update_data)
        self.assertFalse(result)

    async def test_update_note_not_found(self):
        update_data = NoteUpdate(note_text="Non-existent update")
        result = await NoteService.update_note(9999, update_data)  # invalid ID
        self.assertFalse(result)

    #### DELETE
    async def test_delete_note_success(self):
        await NoteService.create_note(self.patient_id, self.note_data)
        notes = await NoteService.get_notes()
        note_id = notes[0].id

        result = await NoteService.delete_note_by_id(note_id)
        self.assertTrue(result)

        remaining = await NoteService.get_notes()
        self.assertEqual(len(remaining), 0)

    async def test_delete_note_not_found(self):
        result = await NoteService.delete_note_by_id(9999)
        self.assertFalse(result)


class TestAttachmentsService(IsolatedAsyncioTestCase):
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
        )
        await PatientService.create_patient(self.minimal_patient)
        patients = await PatientService.get_patients()
        self.patient_id = patients[0].id

        # A valid attachment to use
        self.attachment_data = AttachmentCreate(
            filename="test_document.pdf",
            type="PDF",
            url="https://example.com/test_document.pdf",
            document_type="Lab Report",
            is_local=False,
            original_url=None,
            file_size=1024,
            mime_type="application/pdf",
        )

    async def asyncTearDown(self) -> None:
        await PatientService.delete_patient("Jim", "Doe")
        await database.disconnect()

    #### CREATE
    async def test_create_attachment_success(self):
        result = await AttachmentService.create_attachment(
            self.patient_id, self.attachment_data
        )
        self.assertTrue(result)

        attachments = await AttachmentService.get_attachments()
        self.assertGreaterEqual(len(attachments), 1)
        self.assertEqual(attachments[0].filename, "test_document.pdf")

    #### GET
    async def test_get_attachments_empty(self):
        attachments = await AttachmentService.get_attachments()
        self.assertIsInstance(attachments, list)
        self.assertEqual(len(attachments), 0)

    async def test_get_attachments_by_patient(self):
        await AttachmentService.create_attachment(
            self.patient_id, self.attachment_data
        )
        await AttachmentService.create_attachment(
            self.patient_id,
            AttachmentCreate(
                filename="second_document.pdf",
                type="PDF",
                url="https://example.com/second_document.pdf",
                document_type="Referral",
                is_local=False,
                file_size=2048,
                mime_type="application/pdf",
            ),
        )

        attachments = await AttachmentService.get_attachments_by_patient(
            self.patient_id
        )
        self.assertGreaterEqual(len(attachments), 2)
        self.assertEqual(
            attachments[0].filename, "second_document.pdf"
        )  # newest first

    #### UPDATE
    async def test_update_attachment_success(self):
        await AttachmentService.create_attachment(
            self.patient_id, self.attachment_data
        )
        attachments = await AttachmentService.get_attachments()
        attachment_id = attachments[0].id

        update_data = AttachmentUpdate(filename="updated_document.pdf")
        result = await AttachmentService.update_attachment(
            attachment_id, update_data
        )
        self.assertTrue(result)

        updated_attachments = await AttachmentService.get_attachments()
        self.assertEqual(
            updated_attachments[0].filename, "updated_document.pdf"
        )

    async def test_update_attachment_empty_updates(self):
        await AttachmentService.create_attachment(
            self.patient_id, self.attachment_data
        )
        attachments = await AttachmentService.get_attachments()
        attachment_id = attachments[0].id

        update_data = AttachmentUpdate()
        result = await AttachmentService.update_attachment(
            attachment_id, update_data
        )
        self.assertFalse(result)

    async def test_update_attachment_not_found(self):
        update_data = AttachmentUpdate(filename="nonexistent.pdf")
        result = await AttachmentService.update_attachment(
            9999, update_data
        )  # invalid ID
        self.assertFalse(result)

    #### DELETE
    async def test_delete_attachment_success(self):
        await AttachmentService.create_attachment(
            self.patient_id, self.attachment_data
        )
        attachments = await AttachmentService.get_attachments()
        attachment_id = attachments[0].id

        result = await AttachmentService.delete_attachment_by_id(attachment_id)
        self.assertTrue(result)

        remaining = await AttachmentService.get_attachments()
        self.assertEqual(len(remaining), 0)

    async def test_delete_attachment_not_found(self):
        result = await AttachmentService.delete_attachment_by_id(9999)
        self.assertFalse(result)


class TestInteractionsService(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()

        # Ensure no leftover patients
        await PatientService.delete_patient("Jim", "Doe")

        # Create a minimal patient for linking interactions
        self.minimal_patient = PatientCreate(
            first_name="Jim",
            last_name="Doe",
            dob=date(1990, 3, 22),
        )
        await PatientService.create_patient(self.minimal_patient)
        patients = await PatientService.get_patients()
        self.patient_id = patients[0].id

        # A valid interaction to use
        self.interaction_data = InteractionCreate(
            description="Initial payment",
            date=date(2024, 1, 1),
            referral_id="REF123",
            amount=Decimal("100.00"),
            payment_type="Cash",
            issued="Admin",
        )

    async def asyncTearDown(self) -> None:
        await PatientService.delete_patient("Jim", "Doe")
        await database.disconnect()

    #### CREATE
    async def test_create_interaction_success(self):
        result = await InteractionService.create_interaction(
            self.patient_id, self.interaction_data
        )
        self.assertTrue(result)

        interactions = await InteractionService.get_interactions()
        self.assertGreaterEqual(len(interactions), 1)
        self.assertEqual(interactions[0].description, "Initial payment")

    #### GET
    async def test_get_interactions_empty(self):
        interactions = await InteractionService.get_interactions()
        self.assertIsInstance(interactions, list)
        self.assertEqual(len(interactions), 0)

    async def test_get_interactions_by_patient(self):
        await InteractionService.create_interaction(
            self.patient_id, self.interaction_data
        )
        await InteractionService.create_interaction(
            self.patient_id,
            InteractionCreate(
                description="Follow-up payment",
                date=date(2024, 2, 1),
                referral_id="REF124",
                amount=Decimal("50.00"),
                payment_type="Card",
                issued="Admin",
            ),
        )

        interactions = await InteractionService.get_interactions_by_patient(
            self.patient_id
        )
        self.assertGreaterEqual(len(interactions), 2)
        self.assertEqual(
            interactions[0].description, "Follow-up payment"
        )  # newest first

    #### UPDATE
    async def test_update_interaction_success(self):
        await InteractionService.create_interaction(
            self.patient_id, self.interaction_data
        )
        interactions = await InteractionService.get_interactions()
        interaction_id = interactions[0].id

        update_data = InteractionUpdate(description="Updated payment")
        result = await InteractionService.update_interaction(
            interaction_id, update_data
        )
        self.assertTrue(result)

        updated_interactions = await InteractionService.get_interactions()
        self.assertEqual(
            updated_interactions[0].description, "Updated payment"
        )

    async def test_update_interaction_empty_updates(self):
        await InteractionService.create_interaction(
            self.patient_id, self.interaction_data
        )
        interactions = await InteractionService.get_interactions()
        interaction_id = interactions[0].id

        update_data = InteractionUpdate()
        result = await InteractionService.update_interaction(
            interaction_id, update_data
        )
        self.assertFalse(result)

    async def test_update_interaction_not_found(self):
        update_data = InteractionUpdate(description="Non-existent update")
        result = await InteractionService.update_interaction(9999, update_data)
        self.assertFalse(result)

    #### DELETE
    async def test_delete_interaction_success(self):
        await InteractionService.create_interaction(
            self.patient_id, self.interaction_data
        )
        interactions = await InteractionService.get_interactions()
        interaction_id = interactions[0].id

        result = await InteractionService.delete_interaction_by_id(
            interaction_id
        )
        self.assertTrue(result)

        remaining = await InteractionService.get_interactions()
        self.assertEqual(len(remaining), 0)

    async def test_delete_interaction_not_found(self):
        result = await InteractionService.delete_interaction_by_id(9999)
        self.assertFalse(result)


# -------------------
# Medication Service Tests
# -------------------
class TestMedicationsService(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()

        # Ensure no leftover patients
        await PatientService.delete_patient("Jim", "Doe")

        # Create minimal patient for linking
        self.minimal_patient = PatientCreate(
            first_name="Jim",
            last_name="Doe",
            dob=date(1990, 3, 22),
        )
        await PatientService.create_patient(self.minimal_patient)
        patients = await PatientService.get_patients()
        self.patient_id = patients[0].id

        # Valid medication to use
        self.medication_data = MedicationCreate(
            medication="Aspirin",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 10),
            outcome="Recovered",
        )

    async def asyncTearDown(self) -> None:
        await PatientService.delete_patient("Jim", "Doe")
        await database.disconnect()

    #### CREATE
    async def test_create_medication_success(self):
        result = await MedicationService.create_medication(
            self.patient_id, self.medication_data
        )
        self.assertTrue(result)

        meds = await MedicationService.get_medications()
        self.assertGreaterEqual(len(meds), 1)
        self.assertEqual(meds[0].medication, "Aspirin")

    #### GET
    async def test_get_medications_empty(self):
        meds = await MedicationService.get_medications()
        self.assertIsInstance(meds, list)
        self.assertEqual(len(meds), 0)

    async def test_get_medications_by_patient(self):
        await MedicationService.create_medication(
            self.patient_id, self.medication_data
        )
        await MedicationService.create_medication(
            self.patient_id,
            MedicationCreate(medication="Ibuprofen"),
        )

        meds = await MedicationService.get_medications_by_patient(
            self.patient_id
        )
        self.assertGreaterEqual(len(meds), 2)
        self.assertEqual(meds[0].medication, "Ibuprofen")  # newest first

    #### UPDATE
    async def test_update_medication_success(self):
        await MedicationService.create_medication(
            self.patient_id, self.medication_data
        )
        meds = await MedicationService.get_medications()
        med_id = meds[0].id

        update_data = MedicationUpdate(medication="Paracetamol")
        result = await MedicationService.update_medication(med_id, update_data)
        self.assertTrue(result)

        updated_meds = await MedicationService.get_medications()
        self.assertEqual(updated_meds[0].medication, "Paracetamol")

    async def test_update_medication_empty_updates(self):
        await MedicationService.create_medication(
            self.patient_id, self.medication_data
        )
        meds = await MedicationService.get_medications()
        med_id = meds[0].id

        update_data = MedicationUpdate()
        result = await MedicationService.update_medication(med_id, update_data)
        self.assertFalse(result)

    async def test_update_medication_not_found(self):
        update_data = MedicationUpdate(medication="Non-existent")
        result = await MedicationService.update_medication(9999, update_data)
        self.assertFalse(result)

    #### DELETE
    async def test_delete_medication_success(self):
        await MedicationService.create_medication(
            self.patient_id, self.medication_data
        )
        meds = await MedicationService.get_medications()
        med_id = meds[0].id

        result = await MedicationService.delete_medication_by_id(med_id)
        self.assertTrue(result)

        remaining = await MedicationService.get_medications()
        self.assertEqual(len(remaining), 0)

    async def test_delete_medication_not_found(self):
        result = await MedicationService.delete_medication_by_id(9999)
        self.assertFalse(result)


# -------------------
# Dispensing Service Tests
# -------------------
class TestDispensingService(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()

        await PatientService.delete_patient("Jim", "Doe")
        self.minimal_patient = PatientCreate(
            first_name="Jim", last_name="Doe", dob=date(1990, 3, 22)
        )
        await PatientService.create_patient(self.minimal_patient)
        patients = await PatientService.get_patients()
        self.patient_id = patients[0].id

        self.dispensing_data = DispensingCreate(
            medication="Aspirin",
            rx="RX123",
            quantity=30,
            lot="LOT456",
            product_type="Tablet",
            expiry_date=date(2025, 1, 1),
        )

    async def asyncTearDown(self) -> None:
        await PatientService.delete_patient("Jim", "Doe")
        await database.disconnect()

    #### CREATE
    async def test_create_dispensing_success(self):
        result = await DispensingService.create_dispensing(
            self.patient_id, self.dispensing_data
        )
        self.assertTrue(result)
        records = await DispensingService.get_dispensing()
        self.assertGreaterEqual(len(records), 1)
        self.assertEqual(records[0].medication, "Aspirin")

    #### GET
    async def test_get_dispensings_empty(self):
        records = await DispensingService.get_dispensing()
        self.assertIsInstance(records, list)
        self.assertEqual(len(records), 0)

    async def test_get_dispensings_by_patient(self):
        await DispensingService.create_dispensing(
            self.patient_id, self.dispensing_data
        )
        await DispensingService.create_dispensing(
            self.patient_id,
            DispensingCreate(medication="Ibuprofen"),
        )

        records = await DispensingService.get_dispensing_by_patient(
            self.patient_id
        )
        self.assertGreaterEqual(len(records), 2)
        self.assertEqual(records[0].medication, "Ibuprofen")  # newest first

    #### UPDATE
    async def test_update_dispensing_success(self):
        await DispensingService.create_dispensing(
            self.patient_id, self.dispensing_data
        )
        records = await DispensingService.get_dispensing()
        record_id = records[0].id

        update_data = DispensingUpdate(medication="Paracetamol")
        result = await DispensingService.update_dispensing(
            record_id, update_data
        )
        self.assertTrue(result)

        updated = await DispensingService.get_dispensing()
        self.assertEqual(updated[0].medication, "Paracetamol")

    async def test_update_dispensing_empty_updates(self):
        await DispensingService.create_dispensing(
            self.patient_id, self.dispensing_data
        )
        records = await DispensingService.get_dispensing()
        record_id = records[0].id

        update_data = DispensingUpdate()
        result = await DispensingService.update_dispensing(
            record_id, update_data
        )
        self.assertFalse(result)

    async def test_delete_dispensing_success(self):
        await DispensingService.create_dispensing(
            self.patient_id, self.dispensing_data
        )
        records = await DispensingService.get_dispensing()
        record_id = records[0].id

        result = await DispensingService.delete_dispensing_by_id(record_id)
        self.assertTrue(result)

        remaining = await DispensingService.get_dispensing()
        self.assertEqual(len(remaining), 0)


# -------------------
# Activity Service Tests
# -------------------
class TestActivitiesService(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()

        await PatientService.delete_patient("Jim", "Doe")
        self.minimal_patient = PatientCreate(
            first_name="Jim", last_name="Doe", dob=date(1990, 3, 22)
        )
        await PatientService.create_patient(self.minimal_patient)
        patients = await PatientService.get_patients()
        self.patient_id = patients[0].id

        self.activity_data = ActivityCreate(
            description="Initial activity",
            date=date(2024, 1, 1),
            time=dt.time(9, 0),
        )

    async def asyncTearDown(self) -> None:
        await PatientService.delete_patient("Jim", "Doe")
        await database.disconnect()

    #### CREATE
    async def test_create_activity_success(self):
        result = await ActivityService.create_activity(
            self.patient_id, self.activity_data
        )
        self.assertTrue(result)
        records = await ActivityService.get_activities()
        self.assertGreaterEqual(len(records), 1)
        self.assertEqual(records[0].description, "Initial activity")

    #### GET
    async def test_get_activities_empty(self):
        records = await ActivityService.get_activities()
        self.assertIsInstance(records, list)
        self.assertEqual(len(records), 0)

    async def test_get_activities_by_patient(self):
        await ActivityService.create_activity(
            self.patient_id, self.activity_data
        )
        await ActivityService.create_activity(
            self.patient_id,
            ActivityCreate(
                description="Follow-up activity",
                date=date(2024, 1, 1),
            ),
        )

        records = await ActivityService.get_activities_by_patient(
            self.patient_id
        )
        self.assertGreaterEqual(len(records), 2)
        self.assertEqual(
            records[0].description, "Follow-up activity"
        )  # newest first

    #### UPDATE
    async def test_update_activity_success(self):
        await ActivityService.create_activity(
            self.patient_id, self.activity_data
        )
        records = await ActivityService.get_activities()
        record_id = records[0].id

        update_data = ActivityUpdate(description="Updated activity")
        result = await ActivityService.update_activity(record_id, update_data)
        self.assertTrue(result)

        updated = await ActivityService.get_activities()
        self.assertEqual(updated[0].description, "Updated activity")

    async def test_update_activity_empty_updates(self):
        await ActivityService.create_activity(
            self.patient_id, self.activity_data
        )
        records = await ActivityService.get_activities()
        record_id = records[0].id

        update_data = ActivityUpdate()
        result = await ActivityService.update_activity(record_id, update_data)
        self.assertFalse(result)

    async def test_delete_activity_success(self):
        await ActivityService.create_activity(
            self.patient_id, self.activity_data
        )
        records = await ActivityService.get_activities()
        record_id = records[0].id

        result = await ActivityService.delete_activity_by_id(record_id)
        self.assertTrue(result)

        remaining = await ActivityService.get_activities()
        self.assertEqual(len(remaining), 0)
