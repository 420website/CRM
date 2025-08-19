import subprocess
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from app.config import settings
from app.schema import Disposition, ReferralSite


client = AsyncIOMotorClient(settings.mongo_url)
db = client[settings.db_name]


# PERMANENT DUPLICATE PREVENTION - Create unique indexes on startup
async def create_unique_indexes():
    """Create unique indexes to permanently prevent duplicate registrations"""
    try:
        # Create unique index on firstName + lastName to prevent any duplicates
        await db.admin_registrations.create_index(
            [("firstName", 1), ("lastName", 1)], unique=True, background=True
        )
        logging.info("✅ Unique index created for admin_registrations")

    except Exception as e:
        # Index might already exist, which is fine
        logging.info(f"Index creation info: {str(e)}")


# PERFORMANCE OPTIMIZATION - Create performance indexes for dashboard queries
async def create_performance_indexes():
    """Create indexes optimized for admin dashboard performance"""
    try:
        # Index for efficient pending registrations queries
        await db.admin_registrations.create_index(
            [("status", 1), ("timestamp", -1)], background=True
        )
        logging.info("✅ Performance index created for pending registrations")

        # Index for efficient name searches
        await db.admin_registrations.create_index(
            [("firstName", "text"), ("lastName", "text")], background=True
        )
        logging.info("✅ Text index created for name searches")

        # Index for disposition and referral site filtering
        await db.admin_registrations.create_index(
            [("disposition", 1), ("referralSite", 1), ("regDate", 1)],
            background=True,
        )
        logging.info("✅ Compound index created for filtering")

        # Index for activities performance
        await db.activities.create_index(
            [("created_at", -1), ("registration_id", 1)], background=True
        )
        logging.info("✅ Performance index created for activities")

        # Index for efficient activity date searches
        await db.activities.create_index(
            [("date", 1), ("registration_id", 1)], background=True
        )
        logging.info("✅ Date index created for activities")

    except Exception as e:
        # Indexes might already exist, which is fine
        logging.info(f"Performance index creation info: {str(e)}")


async def seed_clinical_templates():
    """Ensure default clinical templates exist in database"""
    try:
        # Run template seeding using Node.js directly
        result = subprocess.run(
            ["node", "/app/scripts/seed-templates.js"],
            capture_output=True,
            text=True,
            cwd="/app",
            env={"MONGO_URL": settings.mongo_url, "DB_NAME": settings.db_name},
            # env={
            # **os.environ,
            #     "MONGO_URL": os.environ.get(
            #         "MONGO_URL", "mongodb://localhost:27017"
            #     ),
            #     "DB_NAME": os.environ.get("DB_NAME", "medical_db"),
            # },
        )

        if result.returncode == 0:
            logging.info("✅ Clinical templates seeded successfully")
        else:
            logging.error(f"❌ Template seeding failed: {result.stderr}")

    except Exception as e:
        logging.error(f"❌ Error running template seeding: {str(e)}")


async def seed_notes_templates():
    """Ensure default Notes templates exist in database"""
    try:
        # Run Notes template seeding using Node.js directly
        result = subprocess.run(
            ["node", "/app/scripts/seed-notes-templates.js"],
            capture_output=True,
            text=True,
            cwd="/app",
            env={"MONGO_URL": settings.mongo_url, "DB_NAME": settings.db_name},
            #
            #     **os.environ,
            #     "MONGO_URL": os.environ.get(
            #         "MONGO_URL", "mongodb://localhost:27017"
            #     ),
            #     "DB_NAME": os.environ.get("DB_NAME", "medical_db"),
            # },
        )

        if result.returncode == 0:
            logging.info("✅ Notes templates seeded successfully")
        else:
            logging.error(f"❌ Notes template seeding failed: {result.stderr}")

    except Exception as e:
        logging.error(f"❌ Error running Notes template seeding: {str(e)}")


async def seed_dispositions():
    """Ensure default dispositions exist in database"""
    try:
        # Check if dispositions already exist
        existing_count = await db.dispositions.count_documents({})
        if existing_count > 0:
            logging.info("✅ Dispositions already exist in database")
            return

        # Default dispositions with frequency flags
        default_dispositions = [
            # Most frequently used dispositions
            {"name": "ACTIVE", "is_frequent": True, "is_default": True},
            {"name": "BW RLTS", "is_frequent": True, "is_default": True},
            {"name": "CONSULT REQ", "is_frequent": True, "is_default": True},
            {"name": "DELIVERY", "is_frequent": True, "is_default": True},
            {"name": "DISPENSING", "is_frequent": True, "is_default": True},
            {"name": "PENDING", "is_frequent": True, "is_default": True},
            {"name": "POCT NEG", "is_frequent": True, "is_default": True},
            {"name": "PREVIOUSLY TX", "is_frequent": True, "is_default": True},
            {"name": "SELF CURED", "is_frequent": True, "is_default": True},
            {"name": "SOT", "is_frequent": True, "is_default": True},
            # All other dispositions in alphabetical order
            {"name": "ACTIVE-ALL", "is_frequent": False, "is_default": True},
            {
                "name": "ACTIVE-ALL-NC",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "ACTIVE-ALL-OK",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "ACTIVE-BRIDGE",
                "is_frequent": False,
                "is_default": True,
            },
            {"name": "ACTIVE-JAIL", "is_frequent": False, "is_default": True},
            {"name": "ACTIVE-NC", "is_frequent": False, "is_default": True},
            {"name": "ACTIVE-OK", "is_frequent": False, "is_default": True},
            {"name": "BW ERROR", "is_frequent": False, "is_default": True},
            {"name": "BW REQ", "is_frequent": False, "is_default": True},
            {"name": "BW RLTS-P", "is_frequent": False, "is_default": True},
            {"name": "COMPLETED", "is_frequent": False, "is_default": True},
            {
                "name": "CONSULT-LOCATE",
                "is_frequent": False,
                "is_default": True,
            },
            {"name": "CURED", "is_frequent": False, "is_default": True},
            {"name": "DBS", "is_frequent": False, "is_default": True},
            {"name": "DECEASED", "is_frequent": False, "is_default": True},
            {"name": "DELETED", "is_frequent": False, "is_default": True},
            {"name": "DISCONTINUED", "is_frequent": False, "is_default": True},
            {"name": "DUPLICATE", "is_frequent": False, "is_default": True},
            {"name": "EXTERNAL TX", "is_frequent": False, "is_default": True},
            {"name": "HEALTH CARD", "is_frequent": False, "is_default": True},
            {"name": "HIV (ACTIVE)", "is_frequent": False, "is_default": True},
            {
                "name": "HIV - DISCHARGED",
                "is_frequent": False,
                "is_default": True,
            },
            {"name": "HIV PATIENT", "is_frequent": False, "is_default": True},
            {"name": "HOME VISIT", "is_frequent": False, "is_default": True},
            {"name": "HOUSING", "is_frequent": False, "is_default": True},
            {"name": "INACTIVE", "is_frequent": False, "is_default": True},
            {"name": "JAIL", "is_frequent": False, "is_default": True},
            {
                "name": "LAB APPOINTMENT",
                "is_frequent": False,
                "is_default": True,
            },
            {"name": "LAB REQ", "is_frequent": False, "is_default": True},
            {"name": "LOCATE", "is_frequent": False, "is_default": True},
            {"name": "MD UPDATE", "is_frequent": False, "is_default": True},
            {"name": "MISSING RNA", "is_frequent": False, "is_default": True},
            {"name": "NOT READY", "is_frequent": False, "is_default": True},
            {
                "name": "POCT INCOMPLETE",
                "is_frequent": False,
                "is_default": True,
            },
            {"name": "REFUSED BW", "is_frequent": False, "is_default": True},
            {"name": "REFUSED TX", "is_frequent": False, "is_default": True},
            {
                "name": "REIMBURSEMENT",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "REIMBURSEMENT (SAV)",
                "is_frequent": False,
                "is_default": True,
            },
            {"name": "RX", "is_frequent": False, "is_default": True},
            {"name": "SOT-2 WEEKS", "is_frequent": False, "is_default": True},
            {"name": "SOT-ALL", "is_frequent": False, "is_default": True},
            {"name": "SOT-BRIDGED", "is_frequent": False, "is_default": True},
            {"name": "SOT-CONSULT", "is_frequent": False, "is_default": True},
            {"name": "SOT-HOLD", "is_frequent": False, "is_default": True},
            {"name": "SOT-LOCATE", "is_frequent": False, "is_default": True},
            {"name": "SOT-LOCATED", "is_frequent": False, "is_default": True},
            {"name": "SOT-OW", "is_frequent": False, "is_default": True},
            {
                "name": "SOT-SCHEDULED",
                "is_frequent": False,
                "is_default": True,
            },
            {"name": "TRILLIUM", "is_frequent": False, "is_default": True},
            {"name": "TX PENDING", "is_frequent": False, "is_default": True},
            {"name": "UNABLE TO TX", "is_frequent": False, "is_default": True},
            {"name": "WAIT", "is_frequent": False, "is_default": True},
        ]

        # Create disposition objects and insert them
        disposition_objects = []
        for disp_data in default_dispositions:
            disposition_obj = Disposition(**disp_data)
            disposition_dict = disposition_obj.dict()
            disposition_dict["created_at"] = (
                disposition_obj.created_at.isoformat()
            )
            disposition_dict["updated_at"] = (
                disposition_obj.updated_at.isoformat()
            )
            disposition_objects.append(disposition_dict)

        # Insert all dispositions
        if disposition_objects:
            await db.dispositions.insert_many(disposition_objects)
            logging.info(
                f"✅ Seeded {len(disposition_objects)} default dispositions"
            )

    except Exception as e:
        logging.error(f"❌ Error seeding dispositions: {str(e)}")


async def seed_referral_sites():
    """Ensure default referral sites exist in database"""
    try:
        # Check if referral sites already exist
        existing_count = await db.referral_sites.count_documents({})
        if existing_count > 0:
            logging.info("✅ Referral sites already exist in database")
            return

        # Default referral sites with frequency flags
        default_referral_sites = [
            # Most frequently used referral sites (you can adjust these)
            {
                "name": "Toronto - Outreach",
                "is_frequent": True,
                "is_default": True,
            },
            {
                "name": "Hamilton - Wellington",
                "is_frequent": True,
                "is_default": True,
            },
            {"name": "London - LMP", "is_frequent": True, "is_default": True},
            {
                "name": "Ottawa - Outreach",
                "is_frequent": True,
                "is_default": True,
            },
            {
                "name": "Windsor - Outreach",
                "is_frequent": True,
                "is_default": True,
            },
            # All other referral sites in alphabetical order
            {
                "name": "Barrie - City Centre Pharmacy",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Barrie - John Howard Society of Sir",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Brantford - Outreach",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Hamilton - Homewood Suit",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Kingston - Outreach",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "London - LMP (Night)",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Niagara - Community Health",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Niagara - Crysler House",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Niagara - Summer",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Orillia - Downtown Dispensary",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Orillia - John Howard Society",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Orillia - The Light House",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Toronto - Dixon Hall (Lakeshore)",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Toronto - Margaret's Drop-In",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Toronto - Renascent (Dundas)",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Toronto - Renascent (Whitby)",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Toronto - St. Felix Centre",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Windsor - Downtown Mission",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Windsor - Night",
                "is_frequent": False,
                "is_default": True,
            },
            {
                "name": "Windsor - Salvation Army",
                "is_frequent": False,
                "is_default": True,
            },
        ]

        # Create referral site objects and insert them
        referral_site_objects = []
        for site_data in default_referral_sites:
            referral_site_obj = ReferralSite(**site_data)
            referral_site_dict = referral_site_obj.dict()
            referral_site_dict["created_at"] = (
                referral_site_obj.created_at.isoformat()
            )
            referral_site_dict["updated_at"] = (
                referral_site_obj.updated_at.isoformat()
            )
            referral_site_objects.append(referral_site_dict)

        # Insert all referral sites
        if referral_site_objects:
            await db.referral_sites.insert_many(referral_site_objects)
            logging.info(
                f"✅ Seeded {len(referral_site_objects)} default referral sites"
            )

    except Exception as e:
        logging.error(f"❌ Error seeding referral sites: {str(e)}")


async def backup_templates():
    """Backup all templates and data to persistent storage"""
    try:
        # Backup clinical templates
        clinical_templates = await db.clinical_templates.find({}).to_list(
            length=None
        )
        if clinical_templates:
            backup_path = (
                "/app/persistent-data/backups/clinical-templates-backup.json"
            )
            # Convert ObjectId to string for JSON serialization
            for template in clinical_templates:
                if "_id" in template:
                    del template["_id"]

            with open(backup_path, "w") as f:
                import json

                json.dump(clinical_templates, f, indent=2, default=str)
            print(f"✅ Backed up {len(clinical_templates)} clinical templates")

        # Backup notes templates
        notes_templates = await db.notes_templates.find({}).to_list(
            length=None
        )
        if notes_templates:
            backup_path = (
                "/app/persistent-data/backups/notes-templates-backup.json"
            )
            # Convert ObjectId to string for JSON serialization
            for template in notes_templates:
                if "_id" in template:
                    del template["_id"]

            with open(backup_path, "w") as f:
                import json

                json.dump(notes_templates, f, indent=2, default=str)
            print(f"✅ Backed up {len(notes_templates)} notes templates")

        # Backup dispositions
        dispositions = await db.dispositions.find({}).to_list(length=None)
        if dispositions:
            backup_path = (
                "/app/persistent-data/backups/dispositions-backup.json"
            )
            # Convert ObjectId to string for JSON serialization
            for disposition in dispositions:
                if "_id" in disposition:
                    del disposition["_id"]

            with open(backup_path, "w") as f:
                import json

                json.dump(dispositions, f, indent=2, default=str)
            print(f"✅ Backed up {len(dispositions)} dispositions")

        # Backup referral sites
        referral_sites = await db.referral_sites.find({}).to_list(length=None)
        if referral_sites:
            backup_path = (
                "/app/persistent-data/backups/referral-sites-backup.json"
            )
            # Convert ObjectId to string for JSON serialization
            for site in referral_sites:
                if "_id" in site:
                    del site["_id"]

            with open(backup_path, "w") as f:
                import json

                json.dump(referral_sites, f, indent=2, default=str)
            print(f"✅ Backed up {len(referral_sites)} referral sites")

    except Exception as e:
        print(f"❌ Error backing up templates: {e}")
        raise


# Enhanced backup function
async def backup_client_data():
    """Create a comprehensive backup of all data"""
    try:
        # Run the comprehensive backup script with the correct Python environment
        result = subprocess.run(
            [
                "/root/.venv/bin/python",
                "/app/scripts/comprehensive-backup.py",
                "--backup",
            ],
            capture_output=True,
            text=True,
            cwd="/app/scripts",
        )

        if result.returncode == 0:
            print("✅ Comprehensive backup completed successfully")
            return True
        else:
            print(f"❌ Backup failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False


# Helper function to check if data is test data
def is_test_data(registration_data):
    """Check if registration data appears to be test data"""
    test_patterns = [
        "test",
        "TestConnectivity",
        "TestUser",
        "ConnectivityTest",
        "dummy",
        "sample",
        "demo",
        "fake",
        "mock",
    ]

    # Check name fields
    first_name = (registration_data.get("first_name") or "").lower()
    last_name = (registration_data.get("last_name") or "").lower()
    email = (registration_data.get("email") or "").lower()

    # Check if any field contains test patterns
    for pattern in test_patterns:
        if pattern in first_name or pattern in last_name or pattern in email:
            return True

    # Check for obviously fake emails
    if email and ("test@" in email or "example.com" in email):
        return True

    return False


# Helper function to validate production environment
def validate_production_environment():
    """Validate that we're in a proper production environment"""

    # If explicitly marked as production, check for test data
    if settings.environment == "production":
        try:
            result = subprocess.run(
                [
                    "python3",
                    "/app/scripts/environment-protection.py",
                    "--verify",
                ],
                capture_output=True,
                text=True,
                cwd="/app/scripts",
            )

            if result.returncode != 0:
                print(
                    "WARNING: Production environment contains test data or integrity issues"
                )
                return False

            return True
        except Exception as e:
            print(f"Error validating environment: {e}")
            return False

    return True


# Initialize database on startup
async def initialize_database():
    """Initialize database with indexes and default data"""
    await create_unique_indexes()
    await create_performance_indexes()  # Add performance indexes for dashboard optimization
    await seed_clinical_templates()
    await seed_notes_templates()
    await seed_dispositions()
    await seed_referral_sites()
    await backup_templates()  # Backup after seeding

    # Restore client data if exists but database is empty
    admin_count = await db.admin_registrations.count_documents({})
    if admin_count == 0:
        await restore_client_data_if_exists()


async def restore_client_data_if_exists():
    """Restore client data from backup if it exists"""
    try:
        import os

        backup_path = "/app/persistent-data/client-backups/admin-registrations-latest.json"

        if os.path.exists(backup_path):
            with open(backup_path, "r") as f:
                import json

                admin_registrations = json.load(f)

            if admin_registrations:
                await db.admin_registrations.insert_many(admin_registrations)
                print(
                    f"✅ Restored {len(admin_registrations)} client registrations from backup"
                )

    except Exception as e:
        print(f"❌ Error restoring client data: {e}")
