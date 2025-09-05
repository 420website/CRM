# pyright: reportOptionalMemberAccess=none, reportArgumentType=none
import asyncio
from unittest import IsolatedAsyncioTestCase
from app.webpage.schema import ContactMessageCreate, RegistrationMessageCreate
from app.webpage.services import ContactService, RegisterService
from app.database import database


class TestContactService(IsolatedAsyncioTestCase):
    """Integration tests for ContactService - requires test database setup"""

    async def _cleanup_test_data(self):
        """Clean up any test contact messages by email"""
        test_emails = [
            "test_contact@example.com",
            "duplicate_contact@example.com",
        ]
        async with database.get_transaction() as conn:
            for email in test_emails:
                await conn.execute(
                    "DELETE FROM contact_messages WHERE email = $1", email
                )

    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()
        await self._cleanup_test_data()

    async def asyncTearDown(self) -> None:
        await self._cleanup_test_data()
        await database.disconnect()

    async def test_create_contact_message_success(self):
        """Test successful creation of a contact message"""
        contact = ContactMessageCreate(
            first_name="John",
            last_name="Doe",
            email="test_contact@example.com",
            subject="Test Subject",
            message="This is a test message",
        )

        message_id = await ContactService.create_contact_message(contact)
        self.assertIsNotNone(message_id)

        # Verify it was inserted
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM contact_messages WHERE id = $1", message_id
            )
            self.assertIsNotNone(row)
            self.assertEqual(row["email"], "test_contact@example.com")
            self.assertEqual(row["subject"], "Test Subject")

    async def test_create_contact_message_missing_required_fields(self):
        """Test creating a contact message with missing required fields"""
        # Missing message body should fail at the DB level if NOT NULL
        bad_contact = ContactMessageCreate(
            first_name="Jane",
            last_name="Doe",
            email="test_contact@example.com",
            subject="No message",
            message=None,  # Invalid
        )

        with self.assertRaises(Exception):
            await ContactService.create_contact_message(bad_contact)

    async def test_create_duplicate_contact_message(self):
        """Test inserting duplicate messages is allowed (since no unique constraint on email)"""
        contact = ContactMessageCreate(
            first_name="John",
            last_name="Smith",
            email="duplicate_contact@example.com",
            subject="Duplicate Test",
            message="Message 1",
        )

        id1 = await ContactService.create_contact_message(contact)
        id2 = await ContactService.create_contact_message(contact)

        self.assertNotEqual(id1, id2)  # Both rows inserted


class TestRegisterService(IsolatedAsyncioTestCase):
    """Integration tests for RegisterService - requires test database setup"""

    async def _cleanup_test_data(self):
        """Remove test registration messages by email"""
        test_emails = [
            "test_register@example.com",
            "duplicate_register@example.com",
        ]
        async with database.get_transaction() as conn:
            for email in test_emails:
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

    async def test_create_register_message_success(self):
        """Test successful creation of a registration message"""
        registration = RegistrationMessageCreate(
            first_name="Alice",
            last_name="Smith",
            dob="1990-05-10",
            health_card_number="1234567890",
            phone_number="555-111-2222",
            email="test_register@example.com",
            consent_given=True,
        )

        reg_id = await RegisterService.create_register_message(registration)
        self.assertIsNotNone(reg_id)

        # Verify persistence
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM register_messages WHERE id = $1", reg_id
            )
            self.assertIsNotNone(row)
            self.assertEqual(row["email"], "test_register@example.com")
            self.assertTrue(row["consent_given"])

    async def test_create_register_message_missing_required_fields(self):
        """Test creating a registration with missing required fields"""
        bad_registration = RegistrationMessageCreate(
            first_name="Bob",
            last_name="Jones",
            dob=None,  # Invalid, should fail if NOT NULL
            health_card_number="9876543210",
            phone_number="555-999-8888",
            email="test_register@example.com",
            consent_given=False,
        )

        with self.assertRaises(Exception):
            await RegisterService.create_register_message(bad_registration)

    async def test_create_duplicate_register_message(self):
        """Test duplicate email inserts (allowed unless you enforce unique constraint)"""
        registration = RegistrationMessageCreate(
            first_name="Charlie",
            last_name="Brown",
            dob="1985-02-14",
            health_card_number="5555555555",
            phone_number="555-333-4444",
            email="duplicate_register@example.com",
            consent_given=True,
        )

        id1 = await RegisterService.create_register_message(registration)
        id2 = await RegisterService.create_register_message(registration)

        self.assertNotEqual(id1, id2)  # Both rows inserted
