#!/usr/bin/env python3

import asyncio
import sys
from app.utils import get_env
from app.database import database
from app.authentication.services import UserService
from app.authentication.utils import SecurityService


async def register_admin_user(
    name: str, email: str, password: str, phone: str
):
    await database.connect()

    if await UserService.check_user_exists(email):
        await database.disconnect()
        print("Admin user with given credentials already exists.")
        return

    password_hash = SecurityService.hash_password(password)

    query = """
    INSERT INTO users (first_name, last_name, email, phone_number, role, permissions, password_hash, is_verified)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    RETURNING id;
    """

    # Insert user and get the generated ID
    async with database.get_transaction() as conn:
        row = await conn.fetchrow(
            query,
            name,
            "",
            email,
            phone,
            "admin",
            [
                "client",
                "assessments",
                "medication",
                "dispensing",
                "notes",
                "activities",
                "interactions",
                "attachments",
            ],
            password_hash,
            True,
        )
    await database.disconnect()

    if row and "id" in row:
        print("Admin user created.")
        return

    print("Admin user not created.")


async def main():
    """Main function with menu options."""
    admin_email: str = get_env("ADMIN_EMAIL")
    admin_password: str = get_env("ADMIN_PASSWORD")
    admin_phone: str = get_env("ADMIN_PHONE")

    await register_admin_user(
        "admin1", admin_email, admin_password, admin_phone
    )

    admin_email2: str = get_env("ADMIN_EMAIL2")
    admin_phone2: str = get_env("ADMIN_PHONE2")

    await register_admin_user(
        "admin2", admin_email2, admin_password, admin_phone2
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
