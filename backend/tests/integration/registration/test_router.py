# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportOperatorIssue=none, reportAttributeAccessIssue=none
import asyncio
from decimal import Decimal
from unittest import IsolatedAsyncioTestCase
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials
from app.authentication.router import (
    login,
    register,
    setup_authenticator_mfa,
    verify_authenticator_mfa,
    verify_email,
)
from app.database import minio_client, database
from app.authentication.schemas import (
    LoginRequest,
    MFAVerifiactionCode,
    RegisterRequest,
    UserUpdate,
)
from app.authentication.services import UserService
from app.dependencies import get_current_user, get_user_pending_mfa
import pyotp
from app.registration.router import (
    check_healthcard,
    check_name_dob,
    create_activity,
    create_assessment,
    create_dispensing,
    create_interaction,
    create_medication,
    create_note,
    create_patient,
    delete_activity_by_id,
    delete_assessment_by_id,
    delete_dispensing_by_id,
    delete_interaction_by_id,
    delete_medication_by_id,
    delete_note_by_id,
    delete_patient_by_id,
    delete_patient_by_name,
    get_activities,
    get_activities_by_patient,
    get_activity_by_id,
    get_assessment_by_id,
    get_assessments_by_patient,
    get_dispensing_by_id,
    get_dispensings_by_patient,
    get_interaction_by_id,
    get_interactions_by_patient,
    get_medication_by_id,
    get_medications_by_patient,
    get_note_by_id,
    get_notes_by_patient,
    get_patient,
    get_patients,
    get_patients_by_location,
    update_activity,
    update_assessment,
    update_dispensing,
    update_interaction,
    update_medication,
    update_note,
    update_patient,
    update_patient_status,
)
from app.registration.schemas import (
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
    PatientActivity,
    PatientCreate,
    PatientStatus,
    PatientUpdate,
)
from app.registration.services import (
    AssessmentService,
    MedicationService,
    PatientService,
)

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

    # We'll extract the token from here
    captured_token = {}

    def mock_body(message_obj):
        # Extract token from the HTML content in message_obj.msg
        html_content = message_obj.msg
        # Look for the verification URL in the HTML
        import re

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


###############
# Patient
###############
class TestPatientRouter(IsolatedAsyncioTestCase):
    async def _cleanup_test_data(self):
        """Helper method to clean up test data"""
        # Clean up test patients
        test_names = [
            ("John", "Doe"),
            ("Bobby", "Doe"),
            ("Tim", "Tom"),
            ("Jane", "Smith"),
            ("Jane", "Doe"),
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

    async def asyncSetUp(self) -> None:
        await database.connect()
        await minio_client.connect()

        await UserService.delete_user(email, password)
        user = await self.get_validated_user()

        self.updates = UserUpdate(
            province="Ontario", location_permissions=["All"]
        )

        await UserService.update_user(user.id, self.updates)
        self.user = await UserService.get_user_by_id(user.id)

        asyncio.get_event_loop().set_debug(False)
        await self._cleanup_test_data()

        self.patient_data = PatientCreate(
            first_name="Jim",
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

        self.ontario_patient = PatientCreate(
            first_name="John",
            last_name="Doe",
            dob=date(1990, 3, 22),
            province="Ontario",
            disposition="Active",
            referral_site="Toronto",
            age=30,
            gender="Male",
        )

        self.alberta_patient = PatientCreate(
            first_name="John",
            last_name="Doe",
            dob=date(1990, 3, 22),
            province="Alberta",
            disposition="Active",
            referral_site="Toronto",
            age=30,
            gender="Male",
        )

        self.nunavut_patient = PatientCreate(
            first_name="John",
            last_name="Doe",
            dob=date(1990, 3, 22),
            province="Nunavut",
            disposition="Active",
            referral_site="Toronto",
            age=30,
            gender="Male",
        )

    async def asyncTearDown(self):
        await UserService.delete_user(email, password)

        await minio_client.disconnect()
        await database.disconnect()

    # create patient
    async def test_create_patient_success(self):
        patient_data = PatientCreate(
            first_name="Jim",
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

        result = await create_patient(patient_data, self.user)

        self.assertIn("patient_id", result)
        self.assertIsInstance(result["patient_id"], int)

        # Cleanup
        await PatientService.delete_patient_by_id(result["patient_id"])

    async def test_create_patient_with_minimal_data(self):
        patient_data = PatientCreate(
            first_name="Jane",
            last_name="Smith",
            dob=date(1985, 5, 15),
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )

        result = await create_patient(patient_data, self.user)
        self.assertIn("patient_id", result)

        # Cleanup
        await PatientService.delete_patient_by_id(result["patient_id"])

    async def test_create_patient_with_duplicate_health_card(self):
        patient_data = PatientCreate(
            first_name="Jane",
            last_name="Smith",
            dob=date(1985, 5, 15),
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )

        result = await create_patient(patient_data, self.user)
        self.assertIn("patient_id", result)

        patient_data.first_name = "John"
        with self.assertRaises(HTTPException) as cm:
            await create_patient(patient_data, self.user)

        self.assertEqual(cm.exception.status_code, 409)
        self.assertIn(
            "Health card already exists.",
            str(cm.exception.detail),
        )

        # Cleanup
        await PatientService.delete_patient_by_id(result["patient_id"])

    async def test_create_patient_with_duplicate_health_card_exception(self):
        patient_data = PatientCreate(
            first_name="Jane",
            last_name="Smith",
            dob=date(1985, 5, 15),
            health_card="0000000000",
            health_card_version="NA",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )

        result = await create_patient(patient_data, self.user)
        self.assertIn("patient_id", result)

        # with self.assertRaises(HTTPException) as cm:
        patient_data.first_name = "John"
        result2 = await create_patient(patient_data, self.user)
        self.assertIn("patient_id", result2)

        # Cleanup
        await PatientService.delete_patient_by_id(result["patient_id"])
        await PatientService.delete_patient_by_id(result2["patient_id"])

    async def test_create_patient_with_duplicate_name_dob_force(self):
        patient_data = PatientCreate(
            first_name="Jane",
            last_name="Smith",
            dob=date(1985, 5, 15),
            health_card="0000000000",
            health_card_version="NA",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )

        result = await create_patient(patient_data, self.user)
        self.assertIn("patient_id", result)

        patient_data.force_create = True
        result2 = await create_patient(patient_data, self.user)
        self.assertIn("patient_id", result2)

        # Cleanup
        await PatientService.delete_patient_by_id(result["patient_id"])
        await PatientService.delete_patient_by_id(result2["patient_id"])

    async def test_create_patient_with_duplicate_dob_name(self):
        patient_data = PatientCreate(
            first_name="Jane",
            last_name="Smith",
            dob=date(1985, 5, 15),
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
            age=30,
            gender="Male",
        )

        result = await create_patient(patient_data, self.user)
        self.assertIn("patient_id", result)

        # patient_data.first_name = "John"
        with self.assertRaises(HTTPException) as cm:
            await create_patient(patient_data, self.user)

        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn(
            "Patient with that name and dob already exists.",
            str(cm.exception.detail),
        )

        # Cleanup
        await PatientService.delete_patient_by_id(result["patient_id"])

    # get patients
    async def test_get_patients_success(self):
        result = await create_patient(self.patient_data, self.user)
        patient_id = result["patient_id"]

        result = await get_patients(self.user)
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_patients_empty_list(self):
        result = await get_patients(self.user)

        self.assertIsInstance(result, list)

    # get patient by id
    async def test_get_patient_by_id_success(self):
        result = await create_patient(self.patient_data, self.user)
        patient_id = result["patient_id"]

        result = await get_patient(patient_id, self.user)

        self.assertEqual(result.id, patient_id)
        self.assertEqual(result.first_name, "Jim")
        self.assertEqual(result.last_name, "Doe")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_patient_by_id_not_found(self):
        result = await get_patient(99999, self.user)

        self.assertIsNone(result)

    async def test_get_patients_by_all_with_all_permission(self):
        await PatientService.create_patient(self.ontario_patient)
        await PatientService.create_patient(self.alberta_patient)
        await PatientService.create_patient(self.nunavut_patient)

        patients = await get_patients_by_location(["All"], self.user)

        self.assertEqual(len(patients), 3)

    async def test_get_patients_by_multiple_location_specific_permissions(
        self,
    ):
        updates = UserUpdate(
            province="Ontario", location_permissions=["Alberta", "Ontario"]
        )
        await UserService.update_user(self.user.id, updates)
        user = await UserService.get_user_by_id(self.user.id)

        await PatientService.create_patient(self.ontario_patient)
        await PatientService.create_patient(self.alberta_patient)
        await PatientService.create_patient(self.nunavut_patient)

        patients = await get_patients_by_location(["Alberta", "Ontario"], user)

        self.assertEqual(len(patients), 2)

    async def test_get_patients_by_location_none(self):
        # test
        with self.assertRaises(HTTPException) as cm:
            await get_patients_by_location([], self.user)

        self.assertEqual(cm.exception.status_code, 400)
        self.assertEqual(
            cm.exception.detail, "Atleast one location is required"
        )

    async def test_get_patients_by_location_no_permission(self):
        updates = UserUpdate(province="Ontario", location_permissions=[])
        await UserService.update_user(self.user.id, updates)
        user = await UserService.get_user_by_id(self.user.id)

        with self.assertRaises(HTTPException) as cm:
            await get_patients_by_location(["Alberta"], user)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertEqual(
            cm.exception.detail, "User does not have access to any locations."
        )

    async def test_get_patients_by_location_w_all_permission(self):
        await PatientService.create_patient(self.ontario_patient)
        await PatientService.create_patient(self.alberta_patient)
        await PatientService.create_patient(self.nunavut_patient)

        patients = await get_patients_by_location(["Alberta"], self.user)

        self.assertEqual(len(patients), 1)
        self.assertEqual(patients[0].province, "Alberta")

    async def test_get_patients_by_some_locations(
        self,
    ):
        updates = UserUpdate(
            province="Ontario", location_permissions=["Alberta", "Ontario"]
        )
        await UserService.update_user(self.user.id, updates)
        user = await UserService.get_user_by_id(self.user.id)

        await PatientService.create_patient(self.ontario_patient)
        await PatientService.create_patient(self.alberta_patient)

        patients = await get_patients_by_location(["Ontario"], user)

        self.assertEqual(len(patients), 1)

    async def test_get_patients_by_some_locations_invalid(
        self,
    ):
        updates = UserUpdate(
            province="Ontario", location_permissions=["Alberta", "Ontario"]
        )
        await UserService.update_user(self.user.id, updates)
        user = await UserService.get_user_by_id(self.user.id)

        await PatientService.create_patient(self.ontario_patient)
        await PatientService.create_patient(self.alberta_patient)

        with self.assertRaises(HTTPException) as cm:
            await get_patients_by_location(["Nunuvat"], user)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertEqual(
            cm.exception.detail,
            "User does not have access to all locations requested.",
        )

    async def test_get_patients_by_some_locations_w_all(
        self,
    ):
        await PatientService.create_patient(self.ontario_patient)
        await PatientService.create_patient(self.alberta_patient)

        results = await get_patients_by_location(["Ontario", "All"], self.user)

        self.assertEqual(len(results), 2)

    # delete patient by id
    async def test_delete_patient_by_id_success(self):
        result = await create_patient(self.patient_data, self.user)
        patient_id = result["patient_id"]

        result = await delete_patient_by_id(patient_id, self.user)

        self.assertEqual(result["message"], "Patient deleted successfully.")

    async def test_delete_patient_by_id_not_found(self):
        with self.assertRaises(HTTPException) as cm:
            await delete_patient_by_id(99999, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Patient not found.", str(cm.exception.detail))

    # delete patient by name
    async def test_delete_patient_by_name_success(self):
        result = await create_patient(self.patient_data, self.user)
        # patient_id = result["patient_id"]

        result = await delete_patient_by_name("Jim", "Doe", self.user)

        self.assertEqual(result["message"], "Patient deleted successfully.")

    async def test_delete_patient_by_name_not_found(self):
        with self.assertRaises(HTTPException) as cm:
            await delete_patient_by_name("NonExistent", "Patient", self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Patient not found.", str(cm.exception.detail))

    # update patient
    async def test_update_patient_success(self):
        result = await create_patient(self.patient_data, self.user)
        patient_id = result["patient_id"]

        update_data = PatientUpdate(
            phone1="416-555-9999",
            email="john.updated@example.com",
        )

        result = await update_patient(patient_id, update_data, self.user)

        self.assertEqual(result["message"], "Patient updated successfully.")

        # Verify update
        updated_patient = await get_patient(patient_id, self.user)
        self.assertEqual(updated_patient.phone1, "416-555-9999")
        self.assertEqual(updated_patient.email, "john.updated@example.com")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_update_duplicate_health_card(self):
        patient1 = PatientCreate(
            first_name="Tim",
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

        patient2 = PatientCreate(
            first_name="Timmy",
            last_name="Doe",
            dob=date(1990, 1, 1),
            age=33,
            gender="Male",
            email="jim.doe@example.com",
            phone1="416-555-0123",
            status="pending",
            health_card="1234567898",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
        )

        result = await create_patient(patient1, self.user)
        patient_id1 = result["patient_id"]

        result = await create_patient(patient2, self.user)
        patient_id2 = result["patient_id"]

        update_data = PatientUpdate(health_card=patient1.health_card)

        with self.assertRaises(HTTPException) as cm:
            await update_patient(patient_id2, update_data, self.user)

        self.assertEqual(cm.exception.status_code, 409)
        self.assertIn(
            "Health card already exists.",
            str(cm.exception.detail),
        )
        # Cleanup
        await PatientService.delete_patient_by_id(patient_id1)
        await PatientService.delete_patient_by_id(patient_id2)

    async def test_update_patient_duplicate_name_dob(self):
        patient1 = PatientCreate(
            first_name="Tim",
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

        patient2 = PatientCreate(
            first_name="Timmy",
            last_name="Doe",
            dob=date(1990, 1, 1),
            age=33,
            gender="Male",
            email="jim.doe@example.com",
            phone1="416-555-0123",
            status="pending",
            health_card="1234567898",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
        )

        result = await create_patient(patient1, self.user)
        patient_id1 = result["patient_id"]

        result = await create_patient(patient2, self.user)
        patient_id2 = result["patient_id"]

        update_data = PatientUpdate(first_name=patient1.first_name)

        with self.assertRaises(HTTPException) as cm:
            await update_patient(patient_id2, update_data, self.user)

        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn(
            "Patient with that name and dob already exists.",
            str(cm.exception.detail),
        )

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id1)
        await PatientService.delete_patient_by_id(patient_id2)

    async def test_update_patient_duplicate_name_dob_force(self):
        patient1 = PatientCreate(
            first_name="Tim",
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

        patient2 = PatientCreate(
            first_name="Timmy",
            last_name="Doe",
            dob=date(1990, 1, 1),
            age=33,
            gender="Male",
            email="jim.doe@example.com",
            phone1="416-555-0123",
            status="pending",
            health_card="1234567898",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
        )

        result = await create_patient(patient1, self.user)
        patient_id1 = result["patient_id"]

        result = await create_patient(patient2, self.user)
        patient_id2 = result["patient_id"]

        update_data = PatientUpdate(
            first_name=patient1.first_name,
            force_update=True,
        )

        result = await update_patient(patient_id2, update_data, self.user)

        self.assertEqual(result["message"], "Patient updated successfully.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id1)
        await PatientService.delete_patient_by_id(patient_id2)

    async def test_update_patient_not_found(self):
        update_data = PatientUpdate(phone1="416-555-9999")

        with self.assertRaises(HTTPException) as cm:
            await update_patient(99999, update_data, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn(
            "Patient not found or could not be updated.",
            str(cm.exception.detail),
        )

    # update patient status
    @patch("app.registration.router.EmailService.send", new_callable=MagicMock)
    async def test_update_patient_status_to_finalized(self, _):
        result = await create_patient(self.patient_data, self.user)
        patient_id = result["patient_id"]

        status_data = PatientStatus(status="finalized")
        result = await update_patient_status(
            patient_id,
            status_data,
            self.user,
        )

        self.assertEqual(result["message"], "Patient updated successfully.")

        # Verify status change
        updated_patient = await get_patient(patient_id, self.user)
        self.assertEqual(updated_patient.status, "finalized")
        self.assertIsNotNone(updated_patient.finalized_at)

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_update_patient_status_same_status(self):
        result = await create_patient(self.patient_data, self.user)
        patient_id = result["patient_id"]

        # Try to set same status
        status_data = PatientStatus(status="pending")

        with self.assertRaises(HTTPException) as cm:
            await update_patient_status(patient_id, status_data, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn(
            "Patient status already pending.",
            str(cm.exception.detail),
        )

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_update_patient_status_patient_not_found(self):
        status_data = PatientStatus(status="finalized")

        with self.assertRaises(HTTPException) as cm:
            await update_patient_status(99999, status_data, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Patient not found.", str(cm.exception.detail))

    async def test_update_patient_status_patient_saved(self):
        """Expecting the patient to have a finalized date when saved."""
        result = await create_patient(self.patient_data, self.user)
        patient_id = result["patient_id"]

        status_data = PatientStatus(status="saved")
        result = await update_patient_status(
            patient_id,
            status_data,
            self.user,
        )

        self.assertEqual(result["message"], "Patient updated successfully.")

        # Verify status change
        updated_patient = await get_patient(patient_id, self.user)
        self.assertEqual(updated_patient.status, "saved")
        self.assertIsNotNone(updated_patient.finalized_at)

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_update_patient_status_to_pending(self):
        """Expecting the patient to have a finalized date when saved."""
        result = await create_patient(self.patient_data, self.user)
        patient_id = result["patient_id"]

        status_data = PatientStatus(status="saved")
        result = await update_patient_status(
            patient_id,
            status_data,
            self.user,
        )

        self.assertEqual(result["message"], "Patient updated successfully.")

        # Test
        status_data = PatientStatus(status="pending")
        result = await update_patient_status(
            patient_id,
            status_data,
            self.user,
        )

        # Verify status change
        updated_patient = await get_patient(patient_id, self.user)
        self.assertEqual(updated_patient.status, "pending")
        self.assertIsNotNone(updated_patient.finalized_at)

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_update_patient_status_back_to_submitted(self):
        """Expecting the patient to have a finalized date when saved."""
        result = await create_patient(self.patient_data, self.user)
        patient_id = result["patient_id"]

        status_data = PatientStatus(status="saved")
        result = await update_patient_status(
            patient_id,
            status_data,
            self.user,
        )
        updated_patient_1 = await get_patient(patient_id, self.user)
        self.assertEqual(result["message"], "Patient updated successfully.")

        status_data = PatientStatus(status="pending")
        result = await update_patient_status(
            patient_id,
            status_data,
            self.user,
        )

        # Test
        status_data = PatientStatus(status="saved")
        result = await update_patient_status(
            patient_id,
            status_data,
            self.user,
        )

        # Verify status change
        updated_patient_2 = await get_patient(patient_id, self.user)
        self.assertEqual(updated_patient_2.status, "saved")
        self.assertEqual(
            updated_patient_1.finalized_at, updated_patient_2.finalized_at
        )

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

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
        result = await create_patient(patient, self.user)
        patient_id = result["patient_id"]

        # Test
        identity = IdentityCheck(
            first_name="Jane",
            last_name="Doe",
            dob=date(1990, 3, 22),
        )
        result = await check_name_dob(identity, self.user)
        self.assertTrue(result["exists"])

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

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
        result = await create_patient(patient, self.user)
        patient_id = result["patient_id"]

        # Test
        identity = IdentityCheck(
            first_name="Jane",
            last_name="Doe",
            dob=date(1990, 3, 22),
            id=patient_id,
        )
        result = await check_name_dob(identity, self.user)
        self.assertFalse(result["exists"])

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_check_identity_nonexistant_create(self):
        # Test
        identity = IdentityCheck(
            first_name="Jane",
            last_name="Doe",
            dob=date(1990, 3, 22),
        )
        result = await check_name_dob(identity, self.user)
        self.assertFalse(result["exists"])

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
        result = await create_patient(patient, self.user)
        patient_id = result["patient_id"]

        # Test
        check_data = HealthcardCheck(health_card="1234567890")
        result = await check_healthcard(check_data, self.user)

        self.assertTrue(result["exists"])
        self.assertEqual(result["user"]["id"], patient_id)  # pyright: ignore
        self.assertEqual(
            result["user"]["first_name"],  # pyright: ignore
            patient.first_name,
        )
        self.assertEqual(
            result["user"]["last_name"],  # pyright: ignore
            patient.last_name,
        )

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_check_healthcard_nonexists_create(self):
        # Test
        check_data = HealthcardCheck(health_card="9999999999")
        result = await check_healthcard(check_data)
        self.assertFalse(result["exists"])

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
        result = await create_patient(patient, self.user)
        patient_id = result["patient_id"]

        # Test
        check_data = HealthcardCheck(health_card="1234567890", id=patient_id)
        result = await check_healthcard(check_data)
        self.assertFalse(result["exists"])

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)


###############
# Assessments
###############
class TestPatientAssessmentssRouter(IsolatedAsyncioTestCase):
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

    async def mock_create_assessment(self, patient_id):
        """Helper to create a test for a patient"""
        test_data = AssessmentCreate(
            type="HIV",
            date=date.today(),
            result="Negative",
            tester="Lab Tech",
            data={"hiv_type": "Rapid"},
        )

        await create_assessment(patient_id, test_data, self.user)

        # Get the created test to return its ID
        tests = await get_assessments_by_patient(patient_id, self.user)
        return tests[0].id if tests else None

    async def asyncSetUp(self) -> None:
        await database.connect()

        await UserService.delete_user(email, password)
        self.user = await self.get_validated_user()

        asyncio.get_event_loop().set_debug(False)

        self.patient_data = PatientCreate(
            first_name="Jim",
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

        self.hiv_data = AssessmentCreate(
            type="HIV",
            date=date.today(),
            result="Negative",
            tester="Lab Tech",
            data={"hiv_type": "Rapid"},
        )

        self.hiv_update_data = AssessementUpdate(
            result="Positive", data={"hiv_type": "Type 1"}
        )

    async def asyncTearDown(self):
        await UserService.delete_user(email, password)
        await database.disconnect()

    # create test
    async def test_create_assessment_success(self):
        patient_id = await self.mock_create_patient("John")
        result = await create_assessment(patient_id, self.hiv_data, self.user)

        self.assertEqual(result["message"], "Assessment created successfully.")

        data = await AssessmentService.get_assessments()
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0].type, "HIV")
        self.assertEqual(data[0].date, self.hiv_data.date)
        self.assertEqual(data[0].result, self.hiv_data.result)
        self.assertEqual(data[0].tester, self.hiv_data.tester)
        self.assertEqual(data[0].data, self.hiv_data.data)

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_create_assessment_patient_not_found(self):
        with self.assertRaises(HTTPException) as cm:
            await create_assessment(99999, self.hiv_data, self.user)

        self.assertEqual(cm.exception.status_code, 500)
        self.assertIn("Assessment not created", str(cm.exception.detail))

    # get tests by patient
    async def test_get_assessment_by_patient_success(self):
        patient_id = await self.mock_create_patient("John")
        await self.mock_create_assessment(patient_id)

        result = await get_assessments_by_patient(patient_id, self.user)

        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        self.assertEqual(result[0].type, "HIV")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_assessment_by_patient_empty_list(self):
        patient_id = await self.mock_create_patient("John")

        result = await get_assessments_by_patient(patient_id, self.user)

        self.assertIsInstance(result, list)

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_assessmentss_by_patient_not_found(self):
        result = await get_assessments_by_patient(99999, self.user)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    # get test by id
    async def test_get_assessment_by_id_success(self):
        patient_id = await self.mock_create_patient("John")
        test_id = await self.mock_create_assessment(patient_id)

        result = await get_assessment_by_id(patient_id, test_id, self.user)

        self.assertEqual(result.id, test_id)
        self.assertEqual(result.patient_id, patient_id)
        self.assertEqual(result.type, "HIV")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_assessment_by_id_not_found(self):
        patient_id = await self.mock_create_patient("John")

        with self.assertRaises(HTTPException) as cm:
            await get_assessment_by_id(patient_id, 99999, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Assessment not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_assessment_by_id_wrong_patient(self):
        patient_id1 = await self.mock_create_patient("Tim")
        patient_id2 = await self.mock_create_patient("John")
        test_id = await self.mock_create_assessment(patient_id1)

        # Try to get test from patient1 using patient2's ID
        with self.assertRaises(HTTPException) as cm:
            await get_assessment_by_id(patient_id2, test_id, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Assessment not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id1)
        await PatientService.delete_patient_by_id(patient_id2)

    # delete test by id
    async def test_delete_assessment_by_id_success(self):
        patient_id = await self.mock_create_patient("Tim")
        test_id = await self.mock_create_assessment(patient_id)

        result = await delete_assessment_by_id(patient_id, test_id, self.user)

        self.assertEqual(result["message"], "Assessment deleted successfully.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_delete_assessment_by_id_not_found(self):
        patient_id = await self.mock_create_patient("John")

        with self.assertRaises(HTTPException) as cm:
            await delete_assessment_by_id(patient_id, 99999, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Assessment not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_delete_assessment_by_id_wrong_patient(self):
        patient_id1 = await self.mock_create_patient("Tim")
        patient_id2 = await self.mock_create_patient("John")
        test_id = await self.mock_create_assessment(patient_id1)

        # Try to delete test from patient1 using patient2's ID
        with self.assertRaises(HTTPException) as cm:
            await delete_assessment_by_id(patient_id2, test_id, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Assessment not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id1)
        await PatientService.delete_patient_by_id(patient_id2)

    # update test
    async def test_update_assessment_success(self):
        patient_id = await self.mock_create_patient("John")
        id = await self.mock_create_assessment(patient_id)

        hiv_update_data = AssessementUpdate(
            result="Positive", data={"hiv_type": "Type 1"}
        )
        result = await update_assessment(
            patient_id, id, hiv_update_data, self.user
        )

        self.assertEqual(result["message"], "Assessment updated successfully.")

        # Verify update
        updated_test = await get_assessment_by_id(patient_id, id, self.user)
        self.assertEqual(updated_test.result, "Positive")
        self.assertEqual(updated_test.data, {"hiv_type": "Type 1"})

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_update_assessment_not_found(self):
        patient_id = await self.mock_create_patient("John")

        with self.assertRaises(HTTPException) as cm:
            await update_assessment(
                patient_id, 99999, self.hiv_update_data, self.user
            )

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Assessment not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_update_assessment_wrong_patient(self):
        patient_id1 = await self.mock_create_patient("Tim")
        patient_id2 = await self.mock_create_patient("John")
        id = await self.mock_create_assessment(patient_id1)

        # Try to update test from patient1 using patient2's ID
        with self.assertRaises(HTTPException) as cm:
            await update_assessment(
                patient_id2, id, self.hiv_update_data, self.user
            )

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Assessment not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id1)
        await PatientService.delete_patient_by_id(patient_id2)


###############
# Notes
###############
class TestPatientNotesRouter(IsolatedAsyncioTestCase):
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
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
        )

        result = await create_patient(patient_data, self.user)
        return result["patient_id"]

    async def mock_create_note(self, patient_id):
        """Helper to create a note for a patient"""
        note_data = NoteCreate(
            note_text="Patient consultation notes",
            template_type="consultation",
            note_date=date.today(),
        )

        await create_note(patient_id, note_data, self.user)

        # Get the created note to return its ID
        notes = await get_notes_by_patient(patient_id, self.user)
        return notes[0].id if notes else None

    async def asyncSetUp(self) -> None:
        await database.connect()
        await UserService.delete_user(email, password)
        self.user = await self.get_validated_user()

        asyncio.get_event_loop().set_debug(False)

        self.patient_data = PatientCreate(
            first_name="Jim",
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

        self.note_data = NoteCreate(
            note_text="Patient consultation notes",
            template_type="consultation",
            note_date=date.today(),
        )

        self.note_update_data = NoteUpdate(
            note_text="Updated consultation notes", template_type="follow_up"
        )

    async def asyncTearDown(self):
        await UserService.delete_user(email, password)
        await database.disconnect()

    async def test_create_note_success(self):
        patient_id = await self.mock_create_patient("Jim")
        result = await create_note(patient_id, self.note_data, self.user)

        self.assertEqual(result["message"], "Note created successfully.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_notes_by_patient_success(self):
        patient_id = await self.mock_create_patient("Jim")
        await self.mock_create_note(patient_id)

        result = await get_notes_by_patient(patient_id, self.user)

        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        self.assertEqual(result[0].note_text, "Patient consultation notes")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_note_by_id_success(self):
        patient_id = await self.mock_create_patient("Jim")
        note_id = await self.mock_create_note(patient_id)

        result = await get_note_by_id(patient_id, note_id, self.user)

        self.assertEqual(result.id, note_id)
        self.assertEqual(result.patient_id, patient_id)
        self.assertEqual(result.note_text, "Patient consultation notes")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_update_note_success(self):
        patient_id = await self.mock_create_patient("Jim")
        note_id = await self.mock_create_note(patient_id)

        result = await update_note(
            patient_id, note_id, self.note_update_data, self.user
        )

        self.assertEqual(result["message"], "Note updated successfully.")

        # Verify update
        updated_note = await get_note_by_id(patient_id, note_id, self.user)
        self.assertEqual(updated_note.note_text, "Updated consultation notes")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_delete_note_by_id_success(self):
        patient_id = await self.mock_create_patient("Jim")
        note_id = await self.mock_create_note(patient_id)

        result = await delete_note_by_id(patient_id, note_id, self.user)

        self.assertEqual(result["message"], "Note deleted successfully.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_note_by_id_not_found(self):
        patient_id = await self.mock_create_patient("Jim")
        with self.assertRaises(HTTPException) as cm:
            await get_note_by_id(patient_id, 99999, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Note not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)


###############
# Interactions
###############
class TestPatientInteractionsRouter(IsolatedAsyncioTestCase):
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

    async def mock_create_patient(self, name: str):
        """Helper to create a test patient using class user"""
        patient_data = PatientCreate(
            first_name="Jim",
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

        result = await create_patient(patient_data, self.user)
        return result["patient_id"]

    async def mock_create_interaction(self, patient_id):
        """Helper to create an interaction for a patient"""
        interaction_data = InteractionCreate(
            description="Follow-up consultation",
            date=date.today(),
            referral_id="REF123",
            amount=Decimal("150.00"),
            payment_type="insurance",
        )

        await create_interaction(patient_id, interaction_data, self.user)

        # Get the created interaction to return its ID
        interactions = await get_interactions_by_patient(patient_id, self.user)
        return interactions[0].id if interactions else None

    async def asyncSetUp(self) -> None:
        await database.connect()
        await UserService.delete_user(email, password)
        self.user = await self.get_validated_user()
        asyncio.get_event_loop().set_debug(False)

        self.patient_data = PatientCreate(
            first_name="Jim",
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

        # Interaction test data
        self.interaction_data = InteractionCreate(
            description="Follow-up consultation",
            date=date.today(),
            referral_id="REF123",
            amount=Decimal("150.00"),
            payment_type="insurance",
        )

        self.interaction_update_data = InteractionUpdate(
            description="Updated consultation notes", amount=Decimal("200.00")
        )

    async def asyncTearDown(self):
        await UserService.delete_user(email, password)
        await database.disconnect()

    async def test_create_interaction_success(self):
        patient_id = await self.mock_create_patient("Jim")
        result = await create_interaction(
            patient_id, self.interaction_data, self.user
        )

        self.assertEqual(
            result["message"], "Interaction created successfully."
        )

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_interactions_by_patient_success(self):
        patient_id = await self.mock_create_patient("Jim")
        await self.mock_create_interaction(patient_id)

        result = await get_interactions_by_patient(patient_id, self.user)

        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        self.assertEqual(result[0].description, "Follow-up consultation")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_interaction_by_id_success(self):
        patient_id = await self.mock_create_patient("Jim")
        interaction_id = await self.mock_create_interaction(patient_id)

        result = await get_interaction_by_id(
            patient_id, interaction_id, self.user
        )

        self.assertEqual(result.id, interaction_id)
        self.assertEqual(result.patient_id, patient_id)
        self.assertEqual(result.description, "Follow-up consultation")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_update_interaction_success(self):
        patient_id = await self.mock_create_patient("Jim")
        interaction_id = await self.mock_create_interaction(patient_id)

        result = await update_interaction(
            patient_id, interaction_id, self.interaction_update_data, self.user
        )

        self.assertEqual(
            result["message"], "Interaction updated successfully."
        )

        # Verify update
        updated_interaction = await get_interaction_by_id(
            patient_id, interaction_id, self.user
        )
        self.assertEqual(
            updated_interaction.description, "Updated consultation notes"
        )
        self.assertEqual(updated_interaction.amount, Decimal("200.00"))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_delete_interaction_by_id_success(self):
        patient_id = await self.mock_create_patient("Jim")
        interaction_id = await self.mock_create_interaction(patient_id)

        result = await delete_interaction_by_id(
            patient_id, interaction_id, self.user
        )

        self.assertEqual(
            result["message"], "Interaction deleted successfully."
        )

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_interaction_by_id_not_found(self):
        patient_id = await self.mock_create_patient("Jim")

        with self.assertRaises(HTTPException) as cm:
            await get_interaction_by_id(patient_id, 99999, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Interaction not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)


###############
# Medication
###############
class TestPatienMedicationsRouter(IsolatedAsyncioTestCase):
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
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
        )

        result = await create_patient(patient_data, self.user)
        return result["patient_id"]

    async def mock_create_medication(self, patient_id):
        """Helper to create a medication for a patient"""
        medication_data = MedicationCreate(
            medication="Lisinopril 10mg",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            outcome="ongoing",
        )

        await create_medication(patient_id, medication_data, self.user)

        # Get the created medication to return its ID
        medications = await get_medications_by_patient(patient_id, self.user)
        return medications[0].id if medications else None

    async def asyncSetUp(self) -> None:
        await database.connect()
        await UserService.delete_user(email, password)
        self.user = await self.get_validated_user()

        asyncio.get_event_loop().set_debug(False)

        self.patient_data = PatientCreate(
            first_name="Jim",
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

        self.medication_data = MedicationCreate(
            medication="Lisinopril 10mg",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            outcome="ongoing",
        )

        self.medication_update_data = MedicationUpdate(
            medication="Lisinopril 20mg", outcome="completed"
        )

    async def asyncTearDown(self):
        await UserService.delete_user(email, password)
        await database.disconnect()

    async def test_create_medication_success(self):
        patient_id = await self.mock_create_patient("Jim")
        result = await create_medication(
            patient_id, self.medication_data, self.user
        )

        self.assertEqual(result["message"], "Medication created successfully.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_medications_by_patient_success(self):
        patient_id = await self.mock_create_patient("Jim")
        await self.mock_create_medication(patient_id)

        result = await get_medications_by_patient(patient_id, self.user)

        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        self.assertEqual(result[0].medication, "Lisinopril 10mg")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_medication_by_id_success(self):
        patient_id = await self.mock_create_patient("Jim")
        medication_id = await self.mock_create_medication(patient_id)

        result = await get_medication_by_id(
            patient_id, medication_id, self.user
        )

        self.assertEqual(result.id, medication_id)
        self.assertEqual(result.patient_id, patient_id)
        self.assertEqual(result.medication, "Lisinopril 10mg")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_update_medication_success(self):
        patient_id = await self.mock_create_patient("Jim")
        medication_id = await self.mock_create_medication(patient_id)

        result = await update_medication(
            patient_id, medication_id, self.medication_update_data, self.user
        )

        self.assertEqual(result["message"], "Medication updated successfully.")

        # Verify update
        updated_medication = await get_medication_by_id(
            patient_id, medication_id, self.user
        )
        self.assertEqual(updated_medication.medication, "Lisinopril 20mg")
        self.assertEqual(updated_medication.outcome, "completed")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_delete_medication_by_id_success(self):
        patient_id = await self.mock_create_patient("Jim")
        medication_id = await self.mock_create_medication(patient_id)

        result = await delete_medication_by_id(
            patient_id, medication_id, self.user
        )

        self.assertEqual(result["message"], "Medication deleted successfully.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_medication_by_id_not_found(self):
        patient_id = await self.mock_create_patient("Jim")

        with self.assertRaises(HTTPException) as cm:
            await get_medication_by_id(patient_id, 99999, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Medication not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)


# ###############
# # Dispensing
# ###############
class TestPatientDispensingRouter(IsolatedAsyncioTestCase):
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
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
        )

        result = await create_patient(patient_data, self.user)
        return result["patient_id"]

    async def mock_create_dispensing(self, patient_id):
        """Helper to create a dispensing record for a patient"""
        dispensing_data = DispensingCreate(
            medication="Lisinopril",
            rx="RX123456",
            quantity=30,
            lot="LOT789",
            product_type="tablet",
            expiry_date=date.today() + timedelta(days=365),
        )

        await create_dispensing(patient_id, dispensing_data, self.user)

        # Get the created dispensing to return its ID
        dispensings = await get_dispensings_by_patient(patient_id, self.user)
        return dispensings[0].id if dispensings else None

    async def create_medication(self, patient_id: int):
        medication_data = MedicationCreate(
            medication="Lisinopril",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 10),
            outcome="Recovered",
        )

        await MedicationService.create_medication(patient_id, medication_data)

    async def asyncSetUp(self) -> None:
        await database.connect()
        await UserService.delete_user(email, password)
        self.user = await self.get_validated_user()

        asyncio.get_event_loop().set_debug(False)

        self.patient_data = PatientCreate(
            first_name="Jim",
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

        # Dispensing test data
        self.dispensing_data = DispensingCreate(
            medication="Lisinopril",
            rx="RX123456",
            quantity=30,
            lot="LOT789",
            product_type="tablet",
            expiry_date=date.today() + timedelta(days=365),
        )

        self.dispensing_update_data = DispensingUpdate(
            medication="Lisinopril", quantity=60, lot="LOT999"
        )

    async def asyncTearDown(self):
        await UserService.delete_user(email, password)
        await database.disconnect()

    async def test_create_dispensing_success(self):
        patient_id = await self.mock_create_patient("Jim")
        await self.create_medication(patient_id)

        result = await create_dispensing(
            patient_id,
            self.dispensing_data,
            self.user,
        )

        self.assertEqual(result["message"], "Dispensing created successfully.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_create_dispensing_no_medication(self):
        patient_id = await self.mock_create_patient("Jim")

        with self.assertRaises(HTTPException) as cm:
            await create_dispensing(
                patient_id, self.dispensing_data, self.user
            )

        self.assertEqual(cm.exception.status_code, 400)

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_dispensings_by_patient_success(self):
        patient_id = await self.mock_create_patient("Jim")
        await self.create_medication(patient_id)
        await self.mock_create_dispensing(patient_id)

        result = await get_dispensings_by_patient(patient_id, self.user)

        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        self.assertEqual(result[0].medication, "Lisinopril")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_dispensing_by_id_success(self):
        patient_id = await self.mock_create_patient("Jim")
        await self.create_medication(patient_id)
        dispensing_id = await self.mock_create_dispensing(patient_id)

        result = await get_dispensing_by_id(
            patient_id, dispensing_id, self.user
        )

        self.assertEqual(result.id, dispensing_id)
        self.assertEqual(result.patient_id, patient_id)
        self.assertEqual(result.medication, "Lisinopril")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_update_dispensing_success(self):
        patient_id = await self.mock_create_patient("Jim")
        await self.create_medication(patient_id)

        dispensing_id = await self.mock_create_dispensing(patient_id)
        result = await update_dispensing(
            patient_id, dispensing_id, self.dispensing_update_data, self.user
        )

        self.assertEqual(result["message"], "Dispensing updated successfully.")

        # Verify update
        updated_dispensing = await get_dispensing_by_id(
            patient_id, dispensing_id, self.user
        )
        self.assertEqual(updated_dispensing.quantity, 60)
        self.assertEqual(updated_dispensing.lot, "LOT999")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_update_dispensing_nonexistant(self):
        patient_id = await self.mock_create_patient("Jim")
        await self.create_medication(patient_id)

        dispensing_id = await self.mock_create_dispensing(patient_id)

        # Verify update
        self.dispensing_update_data.medication = "Unknown"

        with self.assertRaises(HTTPException) as cm:
            await update_dispensing(
                patient_id,
                dispensing_id,
                self.dispensing_update_data,
                self.user,
            )

        self.assertEqual(cm.exception.status_code, 400)
        self.assertEqual(
            cm.exception.detail,
            "Medication none existant for client please create medication and retry.",
        )

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_delete_dispensing_by_id_success(self):
        patient_id = await self.mock_create_patient("Jim")
        await self.create_medication(patient_id)

        dispensing_id = await self.mock_create_dispensing(patient_id)
        result = await delete_dispensing_by_id(
            patient_id, dispensing_id, self.user
        )

        self.assertEqual(result["message"], "Dispensing deleted successfully.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_dispensing_by_id_not_found(self):
        patient_id = await self.mock_create_patient("Jim")
        await self.create_medication(patient_id)

        with self.assertRaises(HTTPException) as cm:
            await get_dispensing_by_id(patient_id, 99999, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Dispensing not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)


###############
# Activity
###############
class TestPatientActivityRouter(IsolatedAsyncioTestCase):
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

    async def mock_create_patient(self, name: str):
        """Helper to create a test patient using class user"""
        patient_data = PatientCreate(
            first_name=name,
            last_name="Doe",
            dob=date(1990, 1, 1),
            age=33,
            province="Ontario",
            gender="Male",
            email="jim.doe@example.com",
            phone1="416-555-0123",
            status="pending",
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
        )

        result = await create_patient(patient_data, self.user)
        return result["patient_id"]

    async def mock_create_activity(self, patient_id):
        """Helper to create an activity for a patient"""
        activity_data = ActivityCreate(
            date=date.today(),
            time=datetime.now().time(),
            name="Check Blood pressure",
            description="History of low BP.",
        )

        await create_activity(patient_id, activity_data, self.user)

        # Get the created activity to return its ID
        activities = await get_activities_by_patient(patient_id, self.user)
        return activities[0].id if activities else None

    async def asyncSetUp(self) -> None:
        await database.connect()
        await UserService.delete_user(email, password)
        user = await self.get_validated_user()

        self.updates = UserUpdate(
            province="Ontario", location_permissions=["All"]
        )

        await UserService.update_user(user.id, self.updates)
        self.user = await UserService.get_user_by_id(user.id)

        asyncio.get_event_loop().set_debug(False)

        self.patient_data = PatientCreate(
            first_name="Jim",
            last_name="Doe",
            dob=date(1990, 1, 1),
            age=33,
            province="Ontario",
            gender="Male",
            email="jim.doe@example.com",
            phone1="416-555-0123",
            status="pending",
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
        )

        self.ontario_patient = PatientCreate(
            first_name="John",
            last_name="Doe",
            dob=date(1990, 3, 22),
            province="Ontario",
            disposition="Active",
            referral_site="Toronto",
            age=30,
            gender="Male",
        )

        self.alberta_patient = PatientCreate(
            first_name="John",
            last_name="Doe",
            dob=date(1990, 3, 22),
            province="Alberta",
            disposition="Active",
            referral_site="Toronto",
            age=30,
            gender="Male",
        )

        self.nunavut_patient = PatientCreate(
            first_name="John",
            last_name="Doe",
            dob=date(1990, 3, 22),
            province="Nunavut",
            disposition="Active",
            referral_site="Toronto",
            age=30,
            gender="Male",
        )

        # Activity test data
        self.activity_data = ActivityCreate(
            date=date.today(),
            time=datetime.now().time(),
            name="Get Results",
            description="Pick up at 5:00pm",
        )

        self.activity_update_data = ActivityUpdate(
            name="New", description="Updated blood pressure check"
        )

    async def asyncTearDown(self):
        await UserService.delete_user(email, password)
        await database.disconnect()

    async def test_create_activity_success(self):
        patient_id = await self.mock_create_patient("Jim")
        result = await create_activity(
            patient_id, self.activity_data, self.user
        )

        self.assertEqual(result["message"], "Activity created successfully.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_activities_success(self):
        patient_id = await self.mock_create_patient("Jim")
        await self.mock_create_activity(patient_id)

        result = await get_activities(self.user)

        self.assertEqual(1, len(result))
        self.assertIsInstance(result[0], PatientActivity)

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_activities_one_location(self):
        updates = UserUpdate(location_permissions=["Ontario"])
        await UserService.update_user(self.user.id, updates)
        user = await UserService.get_user_by_id(self.user.id)

        o_id = await PatientService.create_patient(self.ontario_patient)
        await self.mock_create_activity(o_id)

        a_id = await PatientService.create_patient(self.alberta_patient)
        await self.mock_create_activity(a_id)

        result = await get_activities(user)
        self.assertEqual(1, len(result))
        self.assertIsInstance(result[0], PatientActivity)

        # Cleanup
        await PatientService.delete_patient_by_id(o_id)
        await PatientService.delete_patient_by_id(a_id)

    async def test_get_activities_some_locations(self):
        updates = UserUpdate(location_permissions=["Ontario", "Alberta"])
        await UserService.update_user(self.user.id, updates)
        user = await UserService.get_user_by_id(self.user.id)

        o_id = await PatientService.create_patient(self.ontario_patient)
        await self.mock_create_activity(o_id)

        a_id = await PatientService.create_patient(self.alberta_patient)
        await self.mock_create_activity(a_id)

        result = await get_activities(user)
        self.assertEqual(2, len(result))
        self.assertIsInstance(result[0], PatientActivity)

        # Cleanup
        await PatientService.delete_patient_by_id(o_id)
        await PatientService.delete_patient_by_id(a_id)

    async def test_get_activities_partial_locations(self):
        updates = UserUpdate(location_permissions=["Ontario", "Nunavut"])
        await UserService.update_user(self.user.id, updates)
        user = await UserService.get_user_by_id(self.user.id)

        o_id = await PatientService.create_patient(self.ontario_patient)
        await self.mock_create_activity(o_id)

        a_id = await PatientService.create_patient(self.alberta_patient)
        await self.mock_create_activity(a_id)

        result = await get_activities(user)
        self.assertEqual(1, len(result))
        self.assertIsInstance(result[0], PatientActivity)

        # Cleanup
        await PatientService.delete_patient_by_id(o_id)
        await PatientService.delete_patient_by_id(a_id)

    async def test_get_patients_by_location_none(self):
        updates = UserUpdate(location_permissions=[])
        await UserService.update_user(self.user.id, updates)
        user = await UserService.get_user_by_id(self.user.id)

        # test
        result = await get_activities(user)
        self.assertEqual(len(result), 0)

    async def test_get_activities_by_patient_success(self):
        patient_id = await self.mock_create_patient("Jim")
        await self.mock_create_activity(patient_id)

        result = await get_activities_by_patient(patient_id, self.user)

        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        self.assertEqual(result[0].name, "Check Blood pressure")
        self.assertEqual(result[0].description, "History of low BP.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_activity_by_id_success(self):
        patient_id = await self.mock_create_patient("Jim")
        activity_id = await self.mock_create_activity(patient_id)

        result = await get_activity_by_id(patient_id, activity_id, self.user)

        self.assertEqual(result.id, activity_id)
        self.assertEqual(result.patient_id, patient_id)
        self.assertEqual(result.name, "Check Blood pressure")
        self.assertEqual(result.description, "History of low BP.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_update_activity_success(self):
        patient_id = await self.mock_create_patient("Jim")
        activity_id = await self.mock_create_activity(patient_id)

        result = await update_activity(
            patient_id, activity_id, self.activity_update_data, self.user
        )

        self.assertEqual(result["message"], "Activity updated successfully.")

        # Verify update
        updated_activity = await get_activity_by_id(
            patient_id, activity_id, self.user
        )

        self.assertEqual(
            updated_activity.description, "Updated blood pressure check"
        )
        self.assertEqual(updated_activity.name, "New")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_delete_activity_by_id_success(self):
        patient_id = await self.mock_create_patient("Jim")
        activity_id = await self.mock_create_activity(patient_id)

        result = await delete_activity_by_id(
            patient_id, activity_id, self.user
        )

        self.assertEqual(result["message"], "Activity deleted successfully.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_activity_by_id_not_found(self):
        patient_id = await self.mock_create_patient("Jim")

        with self.assertRaises(HTTPException) as cm:
            await get_activity_by_id(patient_id, 99999, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Activity not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)
