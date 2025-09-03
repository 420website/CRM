from typing import Optional
from app.webpage.schema import ContactMessageCreate, RegistrationMessageCreate
from app.database import database


class ContactService:
    @staticmethod
    async def create_contact_message(
        contact: ContactMessageCreate,
    ) -> Optional[int]:
        query = """
        INSERT INTO contact_messages (
            first_name, last_name, email, subject, message
        )
        VALUES (
            $1, $2, $3, $4, $5 
        )
        RETURNING id; 
        """

        # Insert patient and get the generated ID
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                contact.first_name,
                contact.last_name,
                contact.email,
                contact.subject,
                contact.message,
            )
            if row and "id" in row:
                return row["id"]
            return None

    @staticmethod
    async def delete_contact_message(contact_id: int) -> bool:
        query = """
        DELETE FROM contact_messages
        WHERE id = $1
        RETURNING id;
        """
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, contact_id)
            return row is not None


class RegisterService:
    @staticmethod
    async def create_register_message(registration: RegistrationMessageCreate):
        query = """
        INSERT INTO register_messages (
            first_name, last_name, dob, health_card_number, phone_number, email, consent_given 
        )
        VALUES (
            $1, $2, $3, $4, $5, $6, $7 
        )
        RETURNING id; 
        """

        # Insert patient and get the generated ID
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                registration.first_name,
                registration.last_name,
                registration.dob,
                registration.health_card_number,
                registration.phone_number,
                registration.email,
                registration.consent_given,
            )
            if row and "id" in row:
                return row["id"]
            return None

    @staticmethod
    async def delete_register_message(registration_id: int) -> bool:
        query = """
        DELETE FROM register_messages
        WHERE id = $1
        RETURNING id;
        """
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, registration_id)
            return row is not None
