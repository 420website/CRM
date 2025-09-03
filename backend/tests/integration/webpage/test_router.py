# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportOperatorIssue=none
import asyncio
from datetime import date
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch
from fastapi import HTTPException
from app.webpage.router import register_for_testing, submit_contact_message
from app.webpage.schema import ContactMessageCreate, RegistrationMessageCreate
from app.database import database


class TestMy420RouterEndpoints(IsolatedAsyncioTestCase):
    """Integration tests for My420 router endpoints - requires test database setup"""

    async def _cleanup_test_data(self):
        """Clean up any test contact and registration messages by email"""
        test_emails = [
            "test_endpoint_contact@example.com",
            "test_endpoint_register@example.com",
            "duplicate_endpoint_contact@example.com",
            "duplicate_endpoint_register@example.com",
        ]
        async with database.get_transaction() as conn:
            for email in test_emails:
                await conn.execute(
                    "DELETE FROM contact_messages WHERE email = $1", email
                )
                await conn.execute(
                    "DELETE FROM register_messages WHERE email = $1", email
                )

    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()
        await self._cleanup_test_data()

    async def asyncTearDown(self) -> None:
        await self._cleanup_test_data()
        await database.disconnect()

    # Contact Email
    @patch("app.webpage.router.send_contact_email")
    async def test_submit_contact_message_success(self, mock_send_email):
        """Test successful contact message submission"""
        mock_send_email.return_value = None

        contact = ContactMessageCreate(
            first_name="John",
            last_name="Doe",
            email="test_endpoint_contact@example.com",
            subject="Test Endpoint Subject",
            message="This is a test message for the endpoint",
        )

        response = await submit_contact_message(contact)

        # Verify response structure
        self.assertIn("message", response)
        self.assertIn("contact_id", response)
        self.assertIn("status", response)
        self.assertEqual(response["message"], "Contact successful sent.")
        self.assertEqual(response["status"], "pending")
        self.assertIsNotNone(response["contact_id"])

        # Verify email was called with correct data
        mock_send_email.assert_called_once_with(contact.model_dump())

        # Verify it was inserted into database
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM contact_messages WHERE id = $1",
                response["contact_id"],
            )
            self.assertIsNotNone(row)
            self.assertEqual(row["email"], "test_endpoint_contact@example.com")
            self.assertEqual(row["subject"], "Test Endpoint Subject")

    @patch("app.webpage.router.send_contact_email")
    async def test_submit_contact_message_database_failure(
        self, mock_send_email
    ):
        """Test contact message submission when database insertion fails"""
        mock_send_email.return_value = None

        # Create contact with invalid data that will cause DB failure
        contact = ContactMessageCreate(
            first_name="Jane",
            last_name="Doe",
            email="test_endpoint_contact@example.com",
            subject="Test Subject",
            message="somthing",  # This should cause DB constraint violation
        )

        with self.assertRaises(HTTPException) as context:
            await submit_contact_message(contact)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(
            context.exception.detail, "Contact message not created."
        )

        # Email should still be sent even if DB fails
        mock_send_email.assert_called_once_with(contact.model_dump())

    @patch("app.webpage.router.send_contact_email")
    async def test_submit_contact_message_email_failure(self, mock_send_email):
        """Test contact message submission when email sending fails"""
        # Mock email sending to raise an exception
        mock_send_email.side_effect = Exception("Email service unavailable")

        contact = ContactMessageCreate(
            first_name="Bob",
            last_name="Smith",
            email="test_endpoint_contact@example.com",
            subject="Test Subject",
            message="Test message",
        )

        # Email failure should not prevent the endpoint from working
        # (depending on your error handling strategy)
        with self.assertRaises(Exception):
            await submit_contact_message(contact)

    @patch("app.webpage.router.send_contact_email")
    async def test_submit_contact_message_multiple_submissions(
        self, mock_send_email
    ):
        """Test multiple contact message submissions with same email"""
        mock_send_email.return_value = None

        contact = ContactMessageCreate(
            first_name="Sarah",
            last_name="Connor",
            email="duplicate_endpoint_contact@example.com",
            subject="Multiple Messages",
            message="First message",
        )

        # Submit first message
        response1 = await submit_contact_message(contact)
        self.assertIsNotNone(response1["contact_id"])

        # Submit second message with same email
        contact.message = "Second message"
        response2 = await submit_contact_message(contact)
        self.assertIsNotNone(response2["contact_id"])

        # Both should succeed with different IDs
        self.assertNotEqual(response1["contact_id"], response2["contact_id"])

        # Verify both emails were sent
        self.assertEqual(mock_send_email.call_count, 2)

    @patch("app.webpage.router.send_contact_email")
    async def test_submit_contact_message_consent_not_required(
        self, mock_send_email
    ):
        """Test that contact messages don't require consent field"""
        mock_send_email.return_value = None

        contact = ContactMessageCreate(
            first_name="Lisa",
            last_name="Simpson",
            email="test_endpoint_contact@example.com",
            subject="No Consent Required",
            message="Contact messages don't need consent",
        )

        response = await submit_contact_message(contact)
        self.assertEqual(response["message"], "Contact successful sent.")
        self.assertIsNotNone(response["contact_id"])

    # Register Email
    @patch("app.webpage.router.send_registration_email")
    async def test_register_for_testing_success(self, mock_send_email):
        """Test successful registration submission"""
        mock_send_email.return_value = None

        registration = RegistrationMessageCreate(
            first_name="Alice",
            last_name="Johnson",
            dob=date(1990, 5, 1),
            health_card_number="1234567890",
            phone_number="555-111-2222",
            email="test_endpoint_register@example.com",
            consent_given=True,
        )

        response = await register_for_testing(registration)

        # Verify response structure
        self.assertIn("message", response)
        self.assertIn("registration_id", response)
        self.assertIn("status", response)
        self.assertEqual(response["message"], "Registration successful")
        self.assertEqual(response["status"], "pending")
        self.assertIsNotNone(response["registration_id"])

        # Verify email was called with correct data
        mock_send_email.assert_called_once_with(registration.model_dump())

        # Verify it was inserted into database
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM register_messages WHERE id = $1",
                response["registration_id"],
            )
            self.assertIsNotNone(row)
            self.assertEqual(
                row["email"], "test_endpoint_register@example.com"
            )
            self.assertTrue(row["consent_given"])

    @patch("app.webpage.router.send_registration_email")
    async def test_register_for_testing_database_failure(
        self, mock_send_email
    ):
        """Test registration submission when database insertion fails"""
        mock_send_email.return_value = None

        # Create registration with invalid data that will cause DB failure
        registration = RegistrationMessageCreate(
            first_name="Charlie",
            last_name="Brown",
            dob=None,  # This should cause DB constraint violation
            health_card_number="9876543210",
            phone_number="555-999-8888",
            email="test_endpoint_register@example.com",
            consent_given=False,
        )

        with self.assertRaises(HTTPException) as context:
            await register_for_testing(registration)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(
            context.exception.detail, "Register message not created."
        )

        # Email should still be sent even if DB fails
        mock_send_email.assert_called_once_with(registration.model_dump())

    @patch("app.webpage.router.send_registration_email")
    async def test_register_for_testing_email_failure(self, mock_send_email):
        """Test registration submission when email sending fails"""
        # Mock email sending to raise an exception
        mock_send_email.side_effect = Exception("Email service unavailable")

        registration = RegistrationMessageCreate(
            first_name="David",
            last_name="Wilson",
            dob=date(1990, 5, 1),
            health_card_number="5555555555",
            phone_number="555-333-4444",
            email="test_endpoint_register@example.com",
            consent_given=True,
        )

        # Email failure should not prevent the endpoint from working
        # (depending on your error handling strategy)
        with self.assertRaises(Exception):
            await register_for_testing(registration)

    @patch("app.webpage.router.send_registration_email")
    async def test_register_for_testing_multiple_registrations(
        self, mock_send_email
    ):
        """Test multiple registrations with same email"""
        mock_send_email.return_value = None

        registration = RegistrationMessageCreate(
            first_name="Tom",
            last_name="Hardy",
            dob=date(1990, 5, 1),
            health_card_number="7777777777",
            phone_number="555-777-8888",
            email="duplicate_endpoint_register@example.com",
            consent_given=True,
        )

        # Submit first registration
        response1 = await register_for_testing(registration)
        self.assertIsNotNone(response1["registration_id"])

        # Submit second registration with same email
        registration.phone_number = "555-888-9999"
        response2 = await register_for_testing(registration)
        self.assertIsNotNone(response2["registration_id"])

        # Both should succeed with different IDs
        self.assertNotEqual(
            response1["registration_id"], response2["registration_id"]
        )

        # Verify both emails were sent
        self.assertEqual(mock_send_email.call_count, 2)

    @patch("app.webpage.router.send_registration_email")
    async def test_register_for_testing_consent_required(
        self, mock_send_email
    ):
        """Test that registration requires consent to be True"""
        mock_send_email.return_value = None
