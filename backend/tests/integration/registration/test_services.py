# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportAttributeAccessIssue=none
import asyncio
from decimal import Decimal
from unittest import IsolatedAsyncioTestCase
from asyncpg import UniqueViolationError
from app.common.storage.postgres import database
from app.core.registration.schemas import (
    ActivityCreate,
    ActivityUpdate,
    AssessementUpdate,
    AssessmentCreate,
    DispensingCreate,
    DispensingUpdate,
    HealthcardCheck,
    IdentityCheck,
    InteractionCreate,
    InteractionUpdate,
    MedicationCreate,
    MedicationUpdate,
    NoteCreate,
    NoteUpdate,
    PatientCreate,
    PatientRead,
    PatientUpdate,
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
from datetime import date
import datetime as dt


class TestPatientService(IsolatedAsyncioTestCase):
    async def _cleanup_test_data(self):
        """Helper method to clean up test data"""
        # Clean up test patients
        test_names = [
            ("John", "Doe"),
            ("Bobby", "Doe"),
            ("Tim", "Tom"),
            ("Jane", "Smith"),
            ("Jane", "Doe"),
            ("Bob", "Doe"),
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
        )

        # Minimal PatientCreate instance with only required fields
        self.minimal_patient = PatientCreate(
            first_name="John",
            last_name="Doe",
            dob=date(1990, 3, 22),
            province="Ontario",
            # health_card="1234567890",
            # health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            age=30,
            gender="Male",
        )

        self.minimal_patient2 = PatientCreate(
            first_name="Jane",
            last_name="Smith",
            dob=date(1990, 3, 22),
            province="Alberta",
            health_card="0987654321",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            age=30,
            gender="Male",
        )

        # PatientCreate for testing edge cases
        self.edge_case_patient = PatientCreate(
            first_name="María José",
            last_name="García-González",
            dob=date(2000, 1, 1),
            health_card="1234567890",
            health_card_version="AB",
            province="Alberta",
            # Testing optional fields with various data types
            age=24,
            gender="Female",
            email="maria.garcia@test-email.com",
            phone1="+1-800-555-9999",
            postal_code="K1A 0A6",  # Canadian postal code format
            leave_message=False,
            voicemail=False,
            text=True,
            reg_date=date(2024, 1, 10),
            disposition="Active",
            referral_site="Toronto",
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
        self.assertTrue(patients[0].limited)
        self.assertIsNotNone(patients[0].id)

    async def test_create_patient_limited(self):
        """Test creation of a default patient"""
        self.minimal_patient.limited = True

        # Test
        id = await PatientService.create_patient(self.minimal_patient)

        # Validate
        patients = await PatientService.get_patient_by_id(id)
        self.assertTrue(patients.limited)
        self.assertEqual(patients.first_name, self.minimal_patient.first_name)

    async def test_create_patient_unlimited(self):
        """Test creation of a default patient"""
        self.minimal_patient.limited = False

        # Test
        id = await PatientService.create_patient(self.minimal_patient)

        # Validate
        patients = await PatientService.get_patient_by_id(id)
        self.assertFalse(patients.limited)
        self.assertEqual(patients.first_name, self.minimal_patient.first_name)

    async def test_update_patient_unlimited(self):
        """Test creation of a default patient"""
        id = await PatientService.create_patient(self.minimal_patient)

        # Test
        update_data = PatientUpdate(limited=False)
        await PatientService.update_patient(id, update_data)

        # Validate
        patients = await PatientService.get_patient_by_id(id)
        self.assertFalse(patients.limited)

    async def test_create_patient_duplicate_healthcard(self):
        """Test creation of a default patient"""
        self.minimal_patient.health_card = "1234567890"
        self.minimal_patient.health_card_version = "AB"

        result = await PatientService.create_patient(self.minimal_patient)
        self.assertTrue(result)

        # Test
        with self.assertRaises(Exception) as cm:
            await PatientService.create_patient(self.minimal_patient)

        self.assertIsInstance(cm.exception, UniqueViolationError)
        self.assertEqual(
            cm.exception.detail,
            "Key (health_card)=(1234567890) already exists.",
        )

    async def test_create_patient_duplicate_healthcard_exception(self):
        """Test creation of a default patient"""

        self.minimal_patient.health_card = "0000000000"
        self.minimal_patient.health_card_version = "AB"

        result = await PatientService.create_patient(self.minimal_patient)
        self.assertTrue(result)

        # Test
        self.minimal_patient.first_name = "Bobby"
        result = await PatientService.create_patient(self.minimal_patient)
        self.assertTrue(result)

        patients = await PatientService.get_patients()
        self.assertEqual(len(patients), 2)

    async def test_get_patient_name_dob(self):
        """Test creation of a default patient"""

        result = await PatientService.create_patient(self.minimal_patient)
        self.assertTrue(result)

        # Test
        result = await PatientService.get_patient_by_name_dob(
            self.minimal_patient.first_name,
            self.minimal_patient.last_name,
            self.minimal_patient.dob,
        )

        assert isinstance(result, int)
        self.assertTrue(result > 0)

    async def test_get_patient_name_dob_none(self):
        """Test creation of a default patient"""

        # Test
        result = await PatientService.get_patient_by_name_dob(
            "noname",
            self.minimal_patient.last_name,
            self.minimal_patient.dob,
        )
        self.assertIsNone(result)

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

    async def test_get_patients_by_location(self):
        await PatientService.create_patient(self.minimal_patient)
        await PatientService.create_patient(self.minimal_patient2)

        patients = await PatientService.get_patients_by_location(["Alberta"])

        self.assertEqual(1, len(patients))
        self.assertEqual(
            patients[0].first_name, self.minimal_patient2.first_name
        )
        self.assertEqual(
            patients[0].last_name, self.minimal_patient2.last_name
        )

    async def test_get_patients_by_no_location(self):
        await PatientService.create_patient(self.minimal_patient)
        await PatientService.create_patient(self.minimal_patient2)

        patients = await PatientService.get_patients_by_location([])

        self.assertEqual(patients, [])

    async def test_get_patients_by_locations(self):
        await PatientService.create_patient(self.minimal_patient)
        await PatientService.create_patient(self.minimal_patient2)

        patients = await PatientService.get_patients_by_location(
            ["Alberta", "Ontario"]
        )

        self.assertEqual(2, len(patients))

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

    async def test_get_patient_other(self):
        patient = PatientCreate(
            first_name="John",
            last_name="Doe",
            dob=date(1990, 3, 22),
            health_card="0000000000",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )

        id1 = await PatientService.create_patient(patient)
        id2 = await PatientService.create_patient(patient)

        patients = await PatientService.get_other_patient_name_dob(
            id1,
            patient.first_name,
            patient.last_name,
            patient.dob,
        )

        self.assertEqual(id2, patients)

    async def test_get_patient_no_other(self):
        id = await PatientService.create_patient(self.minimal_patient)

        patients = await PatientService.get_other_patient_name_dob(
            id,
            self.minimal_patient.first_name,
            self.minimal_patient.last_name,
            self.minimal_patient.dob,
        )

        self.assertIsNone(patients)

    # Checks
    async def test_check_identity_exists_create(self):
        patient = PatientCreate(
            first_name="Jane",
            last_name="Doe",
            dob=date(1990, 3, 22),
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )
        id = await PatientService.create_patient(patient)

        # Test
        identity = IdentityCheck(
            first_name="Jane",
            last_name="Doe",
            dob=date(1990, 3, 22),
        )
        result = await PatientService.check_identity(identity)
        self.assertEqual(result.id, id)
        self.assertEqual(result.first_name, patient.first_name)
        self.assertEqual(result.last_name, patient.last_name)

    async def test_check_identity_exists_edit(self):
        patient = PatientCreate(
            first_name="Jane",
            last_name="Doe",
            dob=date(1990, 3, 22),
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )
        id = await PatientService.create_patient(patient)

        # Test
        identity = IdentityCheck(
            first_name="Jane",
            last_name="Doe",
            dob=date(1990, 3, 22),
            id=id,
        )
        result = await PatientService.check_identity(identity)
        self.assertFalse(result)

    async def test_check_identity_nonexistant_create(self):
        # Test
        identity = IdentityCheck(
            first_name="Jane",
            last_name="Doe",
            dob=date(1990, 3, 22),
        )
        result = await PatientService.check_identity(identity)
        self.assertFalse(result)

    async def test_check_healthcard_exists_create(self):
        patient = PatientCreate(
            first_name="Jane",
            last_name="Doe",
            dob=date(1990, 3, 22),
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )
        id = await PatientService.create_patient(patient)

        # Test
        check_data = HealthcardCheck(health_card="1234567890")
        result = await PatientService.check_healthcard(check_data)

        self.assertEqual(result.id, id)
        self.assertEqual(result.first_name, patient.first_name)
        self.assertEqual(result.last_name, patient.last_name)

    async def test_check_healthcard_nonexists_create(self):
        # Test
        check_data = HealthcardCheck(health_card="9999999999")
        result = await PatientService.check_healthcard(check_data)
        self.assertFalse(result)

    async def test_check_healthcard_exists_edit(self):
        patient = PatientCreate(
            first_name="Jane",
            last_name="Doe",
            dob=date(1990, 3, 22),
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )
        id = await PatientService.create_patient(patient)

        # Test
        check_data = HealthcardCheck(health_card="1234567890", id=id)
        result = await PatientService.check_healthcard(check_data)
        self.assertFalse(result)

    async def test_update_patient_status_first_finalization(self):
        patient = PatientCreate(
            first_name="Jane",
            last_name="Doe",
            dob=date(1990, 3, 22),
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )
        id = await PatientService.create_patient(patient)

        # Test
        await PatientService.update_patient_status(id, "finalized", True)
        patient = await PatientService.get_patient_by_id(id)

        self.assertIsNotNone(patient.finalized_at)

    async def test_update_patient_status_notfirst_finalization(self):
        patient = PatientCreate(
            first_name="Jane",
            last_name="Doe",
            dob=date(1990, 3, 22),
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )
        id = await PatientService.create_patient(patient)

        # Test
        await PatientService.update_patient_status(id, "finalized", True)
        result = await PatientService.get_patient_by_id(id)

        await PatientService.update_patient_status(id, "pending", False)
        await PatientService.update_patient_status(id, "finalized", False)
        result2 = await PatientService.get_patient_by_id(id)

        self.assertEqual(result.finalized_at, result2.finalized_at)

    async def test_create_patient_file_id_creation(self):
        patient = PatientCreate(
            first_name="Jane",
            last_name="Doe",
            dob=date(1990, 3, 22),
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )
        id = await PatientService.create_patient(patient)

        # Test
        result = await PatientService.get_patient_by_id(id)
        self.assertEqual(result.file_id, "JD0390")

    async def test_create_patient_file_id_non_creation(self):
        patient = PatientCreate(
            first_name="Jane",
            last_name="Doe",
            dob=date(1990, 3, 22),
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )
        id = await PatientService.create_patient(patient)

        # Test
        result = await PatientService.get_patient_by_id(id)
        self.assertIsNone(result.file_id)

    async def test_create_patient_file_id_update(self):
        patient = PatientCreate(
            first_name="Jane",
            last_name="Doe",
            dob=date(1990, 3, 22),
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )
        id = await PatientService.create_patient(patient)
        result = await PatientService.get_patient_by_id(id)
        self.assertEqual(result.file_id, "JD0390")

        # Test
        update_data = PatientUpdate(
            first_name="Bob",
            dob=date(1985, 6, 15),
            health_card="1234567887",
        )
        await PatientService.update_patient(id, update_data)
        result = await PatientService.get_patient_by_id(id)

        self.assertEqual(result.file_id, "BD0687")

    async def test_create_patient_file_id_update_none(self):
        patient = PatientCreate(
            first_name="Jane",
            last_name="Doe",
            dob=date(1990, 3, 22),
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )
        id = await PatientService.create_patient(patient)
        result = await PatientService.get_patient_by_id(id)
        self.assertEqual(result.file_id, "JD0390")

        # Test
        update_data = PatientUpdate(health_card=None)
        await PatientService.update_patient(id, update_data)
        result = await PatientService.get_patient_by_id(id)

        self.assertIsNone(result.file_id)


# -------------------
# Assessment Service Tests
# -------------------
class TestAssessmentService(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()
        await PatientService.delete_patient("Jim", "Doe")

        # Create a minimal patient for linking tests
        self.minimal_patient = PatientCreate(
            first_name="Jim",
            last_name="Doe",
            dob=date(1990, 3, 22),
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )
        await PatientService.create_patient(self.minimal_patient)
        patients = await PatientService.get_patients()
        self.patient_id = patients[0].id

        # A valid test to use
        self.hcv_data = AssessmentCreate(
            type="HCV",
            date=date(2024, 1, 1),
            result="Negative",
            tester="CM",
        )

        self.hiv_data = AssessmentCreate(
            type="HIV",
            date=date(2024, 1, 1),
            result="Negative",
            tester="CM",
            data={"hiv_type": "Rapid"},
        )

        self.bloodwork_data = AssessmentCreate(
            type="Bloodwork",
            date=date(2024, 1, 1),
            result="Negative",
            tester="CM",
            data={
                "bloodwork_type": "CBC",
                "bloodwork_circles": "2",
                "bloodwork_date_submitted": "2024-1-2",
            },
        )

    async def asyncTearDown(self) -> None:
        await PatientService.delete_patient("Jim", "Doe")
        await database.disconnect()

    #### CREATE
    async def test_create_hcv_success(self):
        result = await AssessmentService.create_assessment(
            self.patient_id, self.hcv_data
        )
        self.assertTrue(result)

        data = await AssessmentService.get_assessments()

        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0].type, "HCV")
        self.assertEqual(data[0].date, self.hcv_data.date)
        self.assertEqual(data[0].result, self.hcv_data.result)
        self.assertEqual(data[0].tester, self.hcv_data.tester)
        self.assertEqual(data[0].data, self.hcv_data.data)

    async def test_create_hiv_success(self):
        result = await AssessmentService.create_assessment(
            self.patient_id, self.hiv_data
        )
        self.assertTrue(result)

        data = await AssessmentService.get_assessments()
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0].type, "HIV")
        self.assertEqual(data[0].date, self.hiv_data.date)
        self.assertEqual(data[0].result, self.hiv_data.result)
        self.assertEqual(data[0].tester, self.hiv_data.tester)
        self.assertEqual(data[0].data, self.hiv_data.data)

    async def test_create_bloodwork_success(self):
        result = await AssessmentService.create_assessment(
            self.patient_id, self.bloodwork_data
        )
        self.assertTrue(result)

        data = await AssessmentService.get_assessments()
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0].type, "Bloodwork")
        self.assertEqual(data[0].date, self.bloodwork_data.date)
        self.assertEqual(data[0].result, self.bloodwork_data.result)
        self.assertEqual(data[0].tester, self.bloodwork_data.tester)
        self.assertEqual(data[0].data, self.bloodwork_data.data)

    #### GET
    async def test_get_assessments_empty(self):
        tests = await AssessmentService.get_assessments()
        self.assertIsInstance(tests, list)
        self.assertEqual(len(tests), 0)

    async def test_get_assessments_by_patient(self):
        await AssessmentService.create_assessment(
            self.patient_id, self.hcv_data
        )
        self.hiv_data.date = date(2025, 1, 1)
        await AssessmentService.create_assessment(
            self.patient_id, self.hiv_data
        )

        data = await AssessmentService.get_assessment_by_patient(
            self.patient_id
        )

        # print(result)
        self.assertGreaterEqual(len(data), 2)
        self.assertEqual(data[0].type, "HIV")
        self.assertEqual(data[0].date, self.hiv_data.date)
        self.assertEqual(data[0].result, self.hiv_data.result)
        self.assertEqual(data[0].tester, self.hiv_data.tester)
        self.assertEqual(data[0].data, self.hiv_data.data)
        self.assertEqual(data[1].type, "HCV")
        self.assertEqual(data[1].date, self.hcv_data.date)
        self.assertEqual(data[1].result, self.hcv_data.result)
        self.assertEqual(data[1].tester, self.hcv_data.tester)
        self.assertEqual(data[1].data, self.hcv_data.data)

    async def test_get_assessment_by_id(self):
        await AssessmentService.create_assessment(
            self.patient_id, self.hcv_data
        )

        data = await AssessmentService.get_assessments()

        # Test
        result = await AssessmentService.get_assessment_by_id(data[0].id)

        self.assertEqual(result.type, "HCV")
        self.assertEqual(result.date, self.hcv_data.date)
        self.assertEqual(result.result, self.hcv_data.result)
        self.assertEqual(result.tester, self.hcv_data.tester)
        self.assertEqual(result.data, self.hcv_data.data)

    #### UPDATE
    async def test_update_assessment_success(self):
        await AssessmentService.create_assessment(
            self.patient_id, self.hcv_data
        )
        data = await AssessmentService.get_assessments()
        id = data[0].id

        update_data = AssessementUpdate(result="Positive")
        result = await AssessmentService.update_assessment(id, update_data)
        self.assertTrue(result)

        updated = await AssessmentService.get_assessments()
        self.assertEqual(updated[0].result, "Positive")

    async def test_update_assessment_json_success(self):
        await AssessmentService.create_assessment(
            self.patient_id, self.hiv_data
        )
        data = await AssessmentService.get_assessments()
        id = data[0].id

        update_data = AssessementUpdate(data={"hiv_type": "Type 2"})
        result = await AssessmentService.update_assessment(id, update_data)
        self.assertTrue(result)

        updated = await AssessmentService.get_assessments()
        self.assertEqual(updated[0].data, {"hiv_type": "Type 2"})

    async def test_update_assessment_json_none_success(self):
        await AssessmentService.create_assessment(
            self.patient_id, self.hiv_data
        )
        data = await AssessmentService.get_assessments()
        id = data[0].id

        update_data = AssessementUpdate(data=None)
        result = await AssessmentService.update_assessment(id, update_data)
        self.assertTrue(result)

        updated = await AssessmentService.get_assessments()
        self.assertEqual(updated[0].data, None)

    async def test_update_assessment_empty_updates(self):
        await AssessmentService.create_assessment(
            self.patient_id, self.hcv_data
        )
        data = await AssessmentService.get_assessments()
        id = data[0].id

        updates = AssessementUpdate()
        result = await AssessmentService.update_assessment(id, updates)
        self.assertFalse(result)

    async def test_update_assessment_not_found(self):
        update_data = AssessementUpdate(result="Positive")
        result = await AssessmentService.update_assessment(
            9999, update_data
        )  # invalid ID
        self.assertFalse(result)

    #### DELETE
    async def test_delete_assessment_success(self):
        await AssessmentService.create_assessment(
            self.patient_id, self.hiv_data
        )
        data = await AssessmentService.get_assessments()
        id = data[0].id

        result = await AssessmentService.delete_assessment_by_id(id)
        self.assertTrue(result)

        remaining = await AssessmentService.get_assessments()
        self.assertEqual(len(remaining), 0)

    async def test_delete_assessment_not_found(self):
        result = await AssessmentService.delete_assessment_by_id(9999)
        self.assertFalse(result)


# -------------------
# Note Service Tests
# -------------------
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
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
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

    async def test_get_notes_by_patient_chronological_order(self):
        """Expecting th  notes to be returned in order of note_date and updated_at."""
        await NoteService.create_note(self.patient_id, self.note_data)
        note = NoteCreate(
            note_text="Follow-up note",
            note_date=date(2025, 11, 1),
            template_type="testing",
        )
        await NoteService.create_note(self.patient_id, note)

        note = NoteCreate(
            note_text="Follow-up note",
            note_date=date(2025, 11, 1),
            template_type="new-testing",
        )
        await NoteService.create_note(self.patient_id, note)

        note = NoteCreate(
            note_text="Follow-up note",
            note_date=date(2025, 10, 1),
            template_type="old-testing",
        )
        await NoteService.create_note(self.patient_id, note)

        # Test
        notes = await NoteService.get_notes_by_patient(self.patient_id)

        # Validation
        self.assertGreaterEqual(len(notes), 3)
        self.assertEqual(notes[0].template_type, "new-testing")
        self.assertEqual(notes[1].template_type, "testing")
        self.assertEqual(notes[2].template_type, "old-testing")

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


# -------------------
# Interaction Service Tests
# -------------------
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
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
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
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
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
            first_name="Jim",
            last_name="Doe",
            dob=date(1990, 3, 22),
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )
        await PatientService.create_patient(self.minimal_patient)
        patients = await PatientService.get_patients()
        self.patient_id = patients[0].id

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

    async def asyncTearDown(self) -> None:
        await PatientService.delete_patient("Jim", "Doe")
        await database.disconnect()

    async def test_check_medication_no_meds(self):
        medication = "Tylenol"

        # Test
        result = await DispensingService.check_medication(
            self.patient_id, medication
        )
        self.assertFalse(result)

    async def test_check_medication_present(self):
        medication_data = MedicationCreate(
            medication="Aspirin",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 10),
            outcome="Recovered",
        )

        await MedicationService.create_medication(
            self.patient_id,
            medication_data,
        )

        # Test
        result = await DispensingService.check_medication(
            self.patient_id, "Aspirin"
        )
        self.assertTrue(result)

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

    # async def test_update_dispensing_empty_updates(self):
    #     await DispensingService.create_dispensing(
    #         self.patient_id, self.dispensing_data
    #     )
    #     records = await DispensingService.get_dispensing()
    #     record_id = records[0].id
    #
    #     update_data = DispensingUpdate(medication=")
    #     result = await DispensingService.update_dispensing(
    #         record_id, update_data
    #     )
    #     self.assertFalse(result)

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
            first_name="Jim",
            last_name="Doe",
            dob=date(1990, 3, 22),
            health_card="0000000000",
            health_card_version="AB",
            reg_date=date(2024, 1, 1),
            province="Ontario",
            disposition="Active",
            referral_site="Toronto",
            age=30,
            gender="Male",
        )

        self.minimal_patient2 = PatientCreate(
            first_name="Jane",
            last_name="Smith",
            dob=date(1990, 3, 22),
            province="Alberta",
            health_card="0987654321",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            age=30,
            gender="Male",
        )

        await PatientService.create_patient(self.minimal_patient)
        patients = await PatientService.get_patients()
        self.patient_id = patients[0].id

        self.activity_data = ActivityCreate(
            date=date(2024, 1, 1),
            time=dt.time(9, 0),
            name="Delivery",
            description="Drop off at door",
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
        self.assertEqual(records[0].name, "Delivery")
        self.assertEqual(records[0].description, "Drop off at door")

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
                date=date(2024, 1, 1),
                name="Follow-up",
                description="Follow-up on lead",
            ),
        )

        records = await ActivityService.get_activities_by_patient(
            self.patient_id
        )
        self.assertGreaterEqual(len(records), 2)
        self.assertEqual(records[0].name, "Follow-up")
        self.assertEqual(records[0].description, "Follow-up on lead")

    async def test_get_activities(self):
        """
        Expect activities to include patient specific date such
        as file_id, reg_date and created_at
        """
        await ActivityService.create_activity(
            self.patient_id, self.activity_data
        )
        await ActivityService.create_activity(
            self.patient_id,
            ActivityCreate(
                date=date(2024, 1, 1),
                name="Follow-up",
                description="Review test results",
            ),
        )

        # TEst
        activities = await ActivityService.get_patient_activities()

        # Validate
        patient = await PatientService.get_patient_by_id(self.patient_id)
        for a in activities:
            self.assertEqual(a.first_name, patient.first_name)
            self.assertEqual(a.last_name, patient.last_name)
            self.assertEqual(a.disposition, patient.disposition)
            self.assertEqual(a.referral_site, patient.referral_site)
            self.assertEqual(a.phone1, patient.phone1)
            self.assertEqual(a.province, patient.province)
            self.assertEqual(a.reg_date, patient.reg_date)
            self.assertEqual(a.file_id, patient.file_id)
            self.assertEqual(a.submitted_date, patient.created_at)
            self.assertEqual(a.status, patient.status)
            self.assertEqual(a.finalized_at, patient.finalized_at)

    async def test_get_activities_location(self):
        id1 = await PatientService.create_patient(self.minimal_patient)
        id2 = await PatientService.create_patient(self.minimal_patient2)

        await ActivityService.create_activity(id1, self.activity_data)
        await ActivityService.create_activity(id2, self.activity_data)

        # Test
        patients = await ActivityService.get_activites_by_location(["Alberta"])
        self.assertEqual(1, len(patients))

        await PatientService.delete_patient("Jane", "Smith")

    async def test_get_activities_locations(self):
        id1 = await PatientService.create_patient(self.minimal_patient)
        id2 = await PatientService.create_patient(self.minimal_patient2)

        await ActivityService.create_activity(id1, self.activity_data)
        await ActivityService.create_activity(id2, self.activity_data)

        # Test
        patients = await ActivityService.get_activites_by_location(
            ["Alberta", "Ontario"]
        )
        self.assertEqual(2, len(patients))

        await PatientService.delete_patient("Jane", "Smith")

    async def test_get_activities_none(self):
        # Test
        patients = await ActivityService.get_activites_by_location(["Nunavut"])
        self.assertEqual(0, len(patients))

        await PatientService.delete_patient("Jane", "Smith")

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
