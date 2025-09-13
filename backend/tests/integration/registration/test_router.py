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

from app.authentication.schemas import (
    LoginRequest,
    MFAVerifiactionCode,
    RegisterRequest,
)
from app.authentication.services import UserService
from app.database import database
from app.dependencies import get_current_user, get_user_pending_mfa
import pyotp
from app.registration.router import (
    create_activity,
    create_attachment,
    create_dispensing,
    create_interaction,
    create_medication,
    create_note,
    create_patient,
    create_test,
    delete_activity_by_id,
    delete_attachment_by_id,
    delete_dispensing_by_id,
    delete_interaction_by_id,
    delete_medication_by_id,
    delete_note_by_id,
    delete_patient_by_id,
    delete_patient_by_name,
    delete_test_by_id,
    get_activities_by_patient,
    get_activity_by_id,
    get_attachment_by_id,
    get_attachments_by_patient,
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
    get_test_by_id,
    get_tests_by_patient,
    update_activity,
    update_attachment,
    update_dispensing,
    update_interaction,
    update_medication,
    update_note,
    update_patient,
    update_patient_status,
    update_test,
)
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
    PatientStatus,
    PatientUpdate,
    TestCreate,
    TestUpdate,
)
from app.registration.services import PatientService

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
        )

    async def asyncTearDown(self):
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


###############
# Tests
###############
email = "test497@example.com"
password = "securepassword123"


class TestPatientTestsRouter(IsolatedAsyncioTestCase):
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
        )

        result = await create_patient(patient_data, self.user)
        return result["patient_id"]

    async def mock_create_test(self, patient_id):
        """Helper to create a test for a patient"""
        test_data = TestCreate(
            test_type="HIV",
            test_date=date.today(),
            hiv_result="Negative",
            hiv_type="Rapid",
            hiv_tester="Lab Tech",
        )

        await create_test(patient_id, test_data, self.user)

        # Get the created test to return its ID
        tests = await get_tests_by_patient(patient_id, self.user)
        return tests[0].id if tests else None

    async def asyncSetUp(self) -> None:
        await database.connect()
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
        )

        self.test_data = TestCreate(
            test_type="HIV",
            test_date=date.today(),
            hiv_result="Negative",
            hiv_type="Rapid",
            hiv_tester="Lab Tech",
        )

        self.test_update_data = TestUpdate(
            hiv_result="Positive", hcv_result="Negative"
        )

    async def asyncTearDown(self):
        await database.disconnect()

    # create test
    async def test_create_test_success(self):
        patient_id = await self.mock_create_patient("John")
        result = await create_test(patient_id, self.test_data, self.user)

        self.assertEqual(result["message"], "Test created successfully.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    # async def test_create_test_patient_not_found(self):
    #     with self.assertRaises(HTTPException) as cm:
    #         await create_test(99999, self.test_data, self.user)
    #
    #     self.assertEqual(cm.exception.status_code, 400)
    #     self.assertIn("Test not created.", str(cm.exception.detail))

    async def test_create_test_with_all_fields(self):
        patient_id = await self.mock_create_patient("John")

        comprehensive_test_data = TestCreate(
            test_type="Comprehensive",
            test_date=date.today(),
            hiv_result="Negative",
            hiv_type="Rapid",
            hiv_tester="CM",
            hcv_result="Negative",
            hcv_tester="CM",
            bloodwork_type="Full Panel",
            bloodwork_circles="5",
            bloodwork_result="Normal",
            bloodwork_date_submitted=date.today(),
            bloodwork_tester="CM",
        )

        result = await create_test(
            patient_id,
            comprehensive_test_data,
            self.user,
        )

        self.assertEqual(result["message"], "Test created successfully.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    # get tests by patient
    async def test_get_tests_by_patient_success(self):
        patient_id = await self.mock_create_patient("John")
        await self.mock_create_test(patient_id)

        result = await get_tests_by_patient(patient_id, self.user)

        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        self.assertEqual(result[0].test_type, "HIV")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_tests_by_patient_empty_list(self):
        patient_id = await self.mock_create_patient("John")

        result = await get_tests_by_patient(patient_id, self.user)

        self.assertIsInstance(result, list)

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_tests_by_patient_not_found(self):
        result = await get_tests_by_patient(99999, self.user)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    # get test by id
    async def test_get_test_by_id_success(self):
        patient_id = await self.mock_create_patient("John")
        test_id = await self.mock_create_test(patient_id)

        result = await get_test_by_id(patient_id, test_id, self.user)

        self.assertEqual(result.id, test_id)
        self.assertEqual(result.patient_id, patient_id)
        self.assertEqual(result.test_type, "HIV")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_test_by_id_not_found(self):
        patient_id = await self.mock_create_patient("John")

        with self.assertRaises(HTTPException) as cm:
            await get_test_by_id(patient_id, 99999, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Test not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_test_by_id_wrong_patient(self):
        patient_id1 = await self.mock_create_patient("Tim")
        patient_id2 = await self.mock_create_patient("John")
        test_id = await self.mock_create_test(patient_id1)

        # Try to get test from patient1 using patient2's ID
        with self.assertRaises(HTTPException) as cm:
            await get_test_by_id(patient_id2, test_id, self.user)
        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Test not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id1)
        await PatientService.delete_patient_by_id(patient_id2)

    # delete test by id
    async def test_delete_test_by_id_success(self):
        patient_id = await self.mock_create_patient("Tim")
        test_id = await self.mock_create_test(patient_id)

        result = await delete_test_by_id(patient_id, test_id, self.user)

        self.assertEqual(result["message"], "Test deleted successfully.")
        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_delete_test_by_id_not_found(self):
        patient_id = await self.mock_create_patient("John")

        with self.assertRaises(HTTPException) as cm:
            await delete_test_by_id(patient_id, 99999, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Test not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_delete_test_by_id_wrong_patient(self):
        patient_id1 = await self.mock_create_patient("Tim")
        patient_id2 = await self.mock_create_patient("John")
        test_id = await self.mock_create_test(patient_id1)

        # Try to delete test from patient1 using patient2's ID
        with self.assertRaises(HTTPException) as cm:
            await delete_test_by_id(patient_id2, test_id, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Test not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id1)
        await PatientService.delete_patient_by_id(patient_id2)

    # update test
    async def test_update_test_success(self):
        patient_id = await self.mock_create_patient("John")
        test_id = await self.mock_create_test(patient_id)

        result = await update_test(
            patient_id, test_id, self.test_update_data, self.user
        )

        self.assertEqual(result["message"], "Test updated successfully.")

        # Verify update
        updated_test = await get_test_by_id(patient_id, test_id, self.user)
        self.assertEqual(updated_test.hiv_result, "Positive")
        self.assertEqual(updated_test.hcv_result, "Negative")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_update_test_not_found(self):
        patient_id = await self.mock_create_patient("John")

        with self.assertRaises(HTTPException) as cm:
            await update_test(
                patient_id, 99999, self.test_update_data, self.user
            )

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Test not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_update_test_wrong_patient(self):
        patient_id1 = await self.mock_create_patient("Tim")
        patient_id2 = await self.mock_create_patient("John")
        test_id = await self.mock_create_test(patient_id1)

        # Try to update test from patient1 using patient2's ID
        with self.assertRaises(HTTPException) as cm:
            await update_test(
                patient_id2, test_id, self.test_update_data, self.user
            )

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Test not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id1)
        await PatientService.delete_patient_by_id(patient_id2)


###############
# Notes
###############
email = "test497@example.com"
password = "securepassword123"


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
# Attachments
###############
email = "test497@example.com"
password = "securepassword123"


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
            health_card="1234567890",
            health_card_version="AB",
        )

        result = await create_patient(patient_data, self.user)
        return result["patient_id"]

    async def mock_create_attachment(self, patient_id):
        """Helper to create an attachment for a patient"""
        attachment_data = AttachmentCreate(
            filename="test_document.pdf",
            type="document",
            url="https://example.com/test_document.pdf",
            document_type="Lab Report",
            original_url="https://example.com/test_document.pdf",
            is_local=True,
        )

        await create_attachment(patient_id, attachment_data, self.user)

        # Get the created attachment to return its ID
        attachments = await get_attachments_by_patient(patient_id, self.user)
        return attachments[0].id if attachments else None

    async def asyncSetUp(self) -> None:
        await database.connect()
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
        )

        # Attachment test data
        self.attachment_data = AttachmentCreate(
            filename="test_document.pdf",
            type="document",
            document_type="lab_report",
            is_local=True,
            url="https://example.com/test_document.pdf",
            original_url="https://example.com/test_document.pdf",
        )

        self.attachment_update_data = AttachmentUpdate(
            filename="updated_document.pdf", type="image"
        )

    async def asyncTearDown(self):
        await database.disconnect()

    async def test_create_attachment_success(self):
        patient_id = await self.mock_create_patient("Jim")
        result = await create_attachment(
            patient_id, self.attachment_data, self.user
        )

        self.assertEqual(result["message"], "Attachment created successfully.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_attachments_by_patient_success(self):
        patient_id = await self.mock_create_patient("Jim")
        await self.mock_create_attachment(patient_id)

        result = await get_attachments_by_patient(patient_id, self.user)

        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        self.assertEqual(result[0].filename, "test_document.pdf")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_attachment_by_id_success(self):
        patient_id = await self.mock_create_patient("Jim")
        attachment_id = await self.mock_create_attachment(patient_id)

        result = await get_attachment_by_id(
            patient_id, attachment_id, self.user
        )

        self.assertEqual(result.id, attachment_id)
        self.assertEqual(result.patient_id, patient_id)
        self.assertEqual(result.filename, "test_document.pdf")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_update_attachment_success(self):
        patient_id = await self.mock_create_patient("Jim")
        attachment_id = await self.mock_create_attachment(patient_id)

        result = await update_attachment(
            patient_id, attachment_id, self.attachment_update_data, self.user
        )

        self.assertEqual(result["message"], "Attachment updated successfully.")

        # Verify update
        updated_attachment = await get_attachment_by_id(
            patient_id, attachment_id, self.user
        )
        self.assertEqual(updated_attachment.filename, "updated_document.pdf")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_delete_attachment_by_id_success(self):
        patient_id = await self.mock_create_patient("Jim")
        attachment_id = await self.mock_create_attachment(patient_id)

        result = await delete_attachment_by_id(
            patient_id, attachment_id, self.user
        )

        self.assertEqual(result["message"], "Attachment deleted successfully.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_attachment_by_id_not_found(self):
        patient_id = await self.mock_create_patient("Jim")

        with self.assertRaises(HTTPException) as cm:
            await get_attachment_by_id(patient_id, 99999, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Attachment not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)


###############
# Interactions
###############
email = "test497@example.com"
password = "securepassword123"


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
email = "test497@example.com"
password = "securepassword123"


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


###############
# Dispensing
###############
email = "test497@example.com"
password = "securepassword123"


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
        )

        result = await create_patient(patient_data, self.user)
        return result["patient_id"]

    async def mock_create_dispensing(self, patient_id):
        """Helper to create a dispensing record for a patient"""
        dispensing_data = DispensingCreate(
            medication="Lisinopril 10mg",
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

    async def asyncSetUp(self) -> None:
        await database.connect()
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
        )

        # Dispensing test data
        self.dispensing_data = DispensingCreate(
            medication="Lisinopril 10mg",
            rx="RX123456",
            quantity=30,
            lot="LOT789",
            product_type="tablet",
            expiry_date=date.today() + timedelta(days=365),
        )

        self.dispensing_update_data = DispensingUpdate(
            quantity=60, lot="LOT999"
        )

    async def asyncTearDown(self):
        await database.disconnect()

    async def test_create_dispensing_success(self):
        patient_id = await self.mock_create_patient("Jim")
        result = await create_dispensing(
            patient_id, self.dispensing_data, self.user
        )

        self.assertEqual(result["message"], "Dispensing created successfully.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_dispensings_by_patient_success(self):
        patient_id = await self.mock_create_patient("Jim")
        await self.mock_create_dispensing(patient_id)

        result = await get_dispensings_by_patient(patient_id, self.user)

        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        self.assertEqual(result[0].medication, "Lisinopril 10mg")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_dispensing_by_id_success(self):
        patient_id = await self.mock_create_patient("Jim")
        dispensing_id = await self.mock_create_dispensing(patient_id)

        result = await get_dispensing_by_id(
            patient_id, dispensing_id, self.user
        )

        self.assertEqual(result.id, dispensing_id)
        self.assertEqual(result.patient_id, patient_id)
        self.assertEqual(result.medication, "Lisinopril 10mg")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_update_dispensing_success(self):
        patient_id = await self.mock_create_patient("Jim")
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

    async def test_delete_dispensing_by_id_success(self):
        patient_id = await self.mock_create_patient("Jim")
        dispensing_id = await self.mock_create_dispensing(patient_id)

        result = await delete_dispensing_by_id(
            patient_id, dispensing_id, self.user
        )

        self.assertEqual(result["message"], "Dispensing deleted successfully.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_dispensing_by_id_not_found(self):
        patient_id = await self.mock_create_patient("Jim")

        with self.assertRaises(HTTPException) as cm:
            await get_dispensing_by_id(patient_id, 99999, self.user)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("Dispensing not found.", str(cm.exception.detail))

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)


###############
# Activity
###############
email = "test497@example.com"
password = "securepassword123"


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
        )

        result = await create_patient(patient_data, self.user)
        return result["patient_id"]

    async def mock_create_activity(self, patient_id):
        """Helper to create an activity for a patient"""
        activity_data = ActivityCreate(
            description="Blood pressure check",
            time=datetime.now().time(),
            date=date.today(),
        )

        await create_activity(patient_id, activity_data, self.user)

        # Get the created activity to return its ID
        activities = await get_activities_by_patient(patient_id, self.user)
        return activities[0].id if activities else None

    async def asyncSetUp(self) -> None:
        await database.connect()
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
        )

        # Activity test data
        self.activity_data = ActivityCreate(
            description="Blood pressure check",
            time=datetime.now().time(),
            date=date.today(),
        )

        self.activity_update_data = ActivityUpdate(
            description="Updated blood pressure check"
        )

    async def asyncTearDown(self):
        await database.disconnect()

    async def test_create_activity_success(self):
        patient_id = await self.mock_create_patient("Jim")
        result = await create_activity(
            patient_id, self.activity_data, self.user
        )

        self.assertEqual(result["message"], "Activity created successfully.")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_activities_by_patient_success(self):
        patient_id = await self.mock_create_patient("Jim")
        await self.mock_create_activity(patient_id)

        result = await get_activities_by_patient(patient_id, self.user)

        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        self.assertEqual(result[0].description, "Blood pressure check")

        # Cleanup
        await PatientService.delete_patient_by_id(patient_id)

    async def test_get_activity_by_id_success(self):
        patient_id = await self.mock_create_patient("Jim")
        activity_id = await self.mock_create_activity(patient_id)

        result = await get_activity_by_id(patient_id, activity_id, self.user)

        self.assertEqual(result.id, activity_id)
        self.assertEqual(result.patient_id, patient_id)
        self.assertEqual(result.description, "Blood pressure check")

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
