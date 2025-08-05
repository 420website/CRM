#!/usr/bin/env python3
"""
Test Data Generator for Medical Platform
Creates realistic test records for pending and submitted client registrations
"""

import asyncio
import os
import sys
from datetime import datetime, date, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
import random
import pytz
from faker import Faker
import json

# Add parent directory to path for imports
sys.path.append('/app')

fake = Faker('en_CA')  # Canadian locale

# Lists of realistic medical platform data
FIRST_NAMES = [
    "Michael", "Sarah", "David", "Emily", "John", "Jessica", "Robert", "Ashley", 
    "James", "Jennifer", "William", "Amanda", "Richard", "Melissa", "Daniel", "Nicole",
    "Matthew", "Elizabeth", "Christopher", "Lisa", "Anthony", "Karen", "Mark", "Nancy",
    "Paul", "Patricia", "Steven", "Linda", "Kenneth", "Donna", "Joshua", "Carol",
    "Andrew", "Michelle", "Brian", "Sandra", "George", "Deborah", "Thomas", "Rachel",
    "Charles", "Carolyn", "Edward", "Janet", "Ronald", "Catherine", "Timothy", "Maria"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell"
]

DISPOSITIONS = [
    "ACTIVE", "REFERRED", "TREATMENT", "FOLLOWUP", "PENDING", "COMPLETED", 
    "DISCHARGED", "CONSULTATION", "MONITORING", "SCREENING"
]

REFERRAL_SITES = [
    "Toronto General Hospital", "Mount Sinai Hospital", "Sunnybrook Hospital", 
    "St. Michael's Hospital", "Women's College Hospital", "Princess Margaret Hospital",
    "The Hospital for Sick Children", "North York General", "Scarborough General",
    "Etobicoke General Hospital", "Humber River Hospital", "Rouge Valley Hospital",
    "Community Health Center", "Family Health Team", "Walk-in Clinic", 
    "Specialty Clinic", "Public Health Unit", "Mobile Testing Unit"
]

PHYSICIANS = [
    "Dr. David Fletcher", "Dr. Sarah Chen", "Dr. Michael Thompson", "Dr. Emily Rodriguez",
    "Dr. James Wilson", "Dr. Lisa Patel", "Dr. Robert Kim", "Dr. Jessica Brown",
    "Dr. Daniel Lee", "Dr. Amanda Singh", "Dr. Mark Johnson", "Dr. Nicole Wong"
]

PROVINCES = ["Ontario", "Quebec", "British Columbia", "Alberta", "Manitoba", "Saskatchewan", "Nova Scotia", "New Brunswick"]

GENDERS = ["Male", "Female", "Non-binary", "Other", "Prefer not to say"]

CITIES = [
    "Toronto", "Ottawa", "Hamilton", "London", "Windsor", "Kitchener", "Oshawa",
    "Barrie", "Kingston", "Guelph", "Cambridge", "Waterloo", "Brantford", "Peterborough"
]

LANGUAGES = ["English", "French"]  # Using only commonly supported languages to avoid MongoDB text index errors

PATIENT_CONSENT = ["Verbal", "Written"]

def generate_phone_number():
    """Generate Canadian phone number in format (XXX) XXX-XXXX"""
    area_codes = ["416", "647", "437", "905", "289", "365", "613", "519", "705", "807"]
    area_code = random.choice(area_codes)
    exchange = random.randint(200, 999)
    number = random.randint(1000, 9999)
    return f"({area_code}) {exchange}-{number}"

def generate_health_card():
    """Generate Ontario health card number (AAAA-BBB-CCC-AA)"""
    return f"{random.randint(1000, 9999)}-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.choice(['ON', 'AB', 'BC', 'MB', 'SK', 'QC', 'NS', 'NB'])}"

def generate_postal_code():
    """Generate Canadian postal code (A1A 1A1)"""
    letters = "ABCDEFGHIJKLMNPRSTUVWXYZ"
    numbers = "0123456789"
    return f"{random.choice(letters)}{random.choice(numbers)}{random.choice(letters)} {random.choice(numbers)}{random.choice(letters)}{random.choice(numbers)}"

def generate_dob():
    """Generate date of birth between 18-80 years old"""
    today = date.today()
    min_age = 18
    max_age = 80
    min_date = today - timedelta(days=max_age * 365)
    max_date = today - timedelta(days=min_age * 365)
    
    random_days = random.randint(0, (max_date - min_date).days)
    return min_date + timedelta(days=random_days)

def generate_reg_date():
    """Generate registration date within last 3 months"""
    today = date.today()
    start_date = today - timedelta(days=90)
    random_days = random.randint(0, 90)
    return start_date + timedelta(days=random_days)

def generate_email(first_name, last_name):
    """Generate realistic email address"""
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "bell.net", "rogers.com"]
    domain = random.choice(domains)
    formats = [
        f"{first_name.lower()}.{last_name.lower()}@{domain}",
        f"{first_name.lower()}{last_name.lower()}@{domain}",
        f"{first_name[0].lower()}{last_name.lower()}@{domain}",
        f"{first_name.lower()}{random.randint(10, 99)}@{domain}"
    ]
    return random.choice(formats)

def generate_address(city):
    """Generate realistic Canadian address"""
    street_numbers = [str(random.randint(1, 9999))]
    if random.random() < 0.3:  # 30% chance of unit number
        unit = f"Unit {random.randint(1, 50)} "
        street_numbers.append(unit)
    
    street_names = [
        "Main Street", "King Street", "Queen Street", "Church Street", "University Ave",
        "Bloor Street", "Yonge Street", "Dundas Street", "College Street", "Bay Street",
        "Front Street", "Richmond Street", "Adelaide Street", "Elm Street", "Oak Avenue",
        "Maple Drive", "Pine Road", "Cedar Lane", "Birch Way", "Willow Court"
    ]
    
    street_name = random.choice(street_names)
    street_num = random.randint(1, 9999)
    
    if len(street_numbers) > 1:
        return f"{street_numbers[1]}{street_num} {street_name}"
    else:
        return f"{street_num} {street_name}"

def generate_special_attention():
    """Generate realistic special attention notes"""
    notes = [
        "Patient requires interpreter services",
        "Mobility assistance needed",
        "Anxiety about blood draws",
        "Previous adverse reaction to medications",
        "Hard of hearing - please speak clearly",
        "Prefers morning appointments",
        "Has transportation limitations",
        "Needs reminder calls",
        "Requires wheelchair access",
        "Diabetic - may need glucose monitoring",
        None, None, None, None  # 40% chance of no special notes
    ]
    return random.choice(notes)

def generate_instructions():
    """Generate realistic instruction notes"""
    instructions = [
        "Fasting required 12 hours before test",
        "Bring all current medications",
        "Contact if symptoms worsen",
        "Follow up in 2 weeks",
        "Schedule follow-up appointment",
        "Lab results will be mailed",
        "Return for additional testing if needed",
        "Maintain current medication regimen",
        None, None, None  # 30% chance of no instructions
    ]
    return random.choice(instructions)

async def create_test_record(status="pending_review"):
    """Create a single test record with realistic data"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    city = random.choice(CITIES)
    
    # Calculate timezone-aware timestamp
    toronto_tz = pytz.timezone('America/Toronto')
    base_time = datetime.now(toronto_tz)
    # Randomize timestamp within last 90 days
    random_days = random.randint(0, 90)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    timestamp = base_time - timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
    
    record = {
        "id": str(uuid.uuid4()),
        "firstName": first_name,
        "lastName": last_name,
        "dob": generate_dob().isoformat(),
        "patientConsent": random.choice(PATIENT_CONSENT),
        "gender": random.choice(GENDERS),
        "province": random.choice(PROVINCES),
        "disposition": random.choice(DISPOSITIONS),
        "aka": None if random.random() < 0.8 else f"{first_name} {fake.first_name()}",
        "age": str(random.randint(18, 80)),
        "regDate": generate_reg_date().isoformat(),
        "healthCard": generate_health_card(),
        "healthCardVersion": str(random.randint(1, 9)),
        "referralSite": random.choice(REFERRAL_SITES),
        "address": generate_address(city),
        "unitNumber": None if random.random() < 0.7 else str(random.randint(1, 50)),
        "city": city,
        "postalCode": generate_postal_code(),
        "phone1": generate_phone_number(),
        "phone2": None if random.random() < 0.8 else generate_phone_number(),
        "ext1": None if random.random() < 0.9 else str(random.randint(100, 9999)),
        "ext2": None,
        "leaveMessage": random.choice([True, False]),
        "voicemail": random.choice([True, False]),
        "text": random.choice([True, False]),
        "preferredTime": random.choice([None, "Morning", "Afternoon", "Evening"]),
        "email": generate_email(first_name, last_name),
        "language": random.choice(LANGUAGES),
        "specialAttention": generate_special_attention(),
        "instructions": generate_instructions(),
        "photo": None,  # No photos for test data
        "summaryTemplate": None,
        "selectedTemplate": "Select",
        "physician": random.choice(PHYSICIANS),
        "rnaAvailable": random.choice(["Yes", "No"]),
        "rnaSampleDate": None if random.random() < 0.7 else generate_reg_date().isoformat(),
        "rnaResult": random.choice(["Positive", "Negative", "Pending"]),
        "coverageType": random.choice(["OHIP", "Private", "Out of Province", "Select"]),
        "referralPerson": None if random.random() < 0.6 else fake.name(),
        "testType": "Tests",
        "hivDate": None if random.random() < 0.8 else generate_reg_date().isoformat(),
        "hivResult": None if random.random() < 0.8 else random.choice(["Negative", "Positive"]),
        "hivType": None if random.random() < 0.9 else random.choice(["Type 1", "Type 2"]),
        "hivTester": random.choice(["CM", "JD", "SP", "MK", "AL"]),
        "timestamp": timestamp,
        "status": status,
        "attachments": []
    }
    
    return record

async def generate_test_data():
    """Generate all test data and insert into database"""
    print("🚀 Starting test data generation...")
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'my420_ca_db')]
    collection = db.admin_registrations
    
    try:
        # Clear any existing test data (optional - comment out if you want to keep existing records)
        print("🗑️  Clearing existing test records...")
        await collection.delete_many({"firstName": {"$in": FIRST_NAMES}})
        
        total_records = []
        
        # Generate 500 pending records
        print("📝 Generating 500 pending records...")
        pending_records = []
        for i in range(500):
            record = await create_test_record(status="pending_review")
            pending_records.append(record)
            if (i + 1) % 50 == 0:
                print(f"   Generated {i + 1}/500 pending records...")
        
        # Generate 1000 submitted records  
        print("📋 Generating 1000 submitted records...")
        submitted_records = []
        for i in range(1000):
            record = await create_test_record(status="completed")
            submitted_records.append(record)
            if (i + 1) % 100 == 0:
                print(f"   Generated {i + 1}/1000 submitted records...")
        
        total_records = pending_records + submitted_records
        
        # Insert in batches to handle potential duplicates
        print("💾 Inserting records into database...")
        batch_size = 100
        inserted_count = 0
        duplicate_count = 0
        
        for i in range(0, len(total_records), batch_size):
            batch = total_records[i:i+batch_size]
            
            # Insert each record individually to handle duplicates
            for record in batch:
                try:
                    await collection.insert_one(record)
                    inserted_count += 1
                except Exception as e:
                    if "duplicate key" in str(e).lower():
                        duplicate_count += 1
                        # Generate new names and try again
                        record["firstName"] = random.choice(FIRST_NAMES)
                        record["lastName"] = random.choice(LAST_NAMES) 
                        record["id"] = str(uuid.uuid4())
                        try:
                            await collection.insert_one(record)
                            inserted_count += 1
                        except:
                            duplicate_count += 1
                    else:
                        print(f"Error inserting record: {e}")
            
            if (i + batch_size) % (batch_size * 5) == 0:
                print(f"   Inserted {min(i + batch_size, len(total_records))}/{len(total_records)} records...")
        
        # Verify insertion
        pending_count = await collection.count_documents({"status": "pending_review"})
        submitted_count = await collection.count_documents({"status": "completed"})
        
        print(f"\n✅ Test data generation completed!")
        print(f"📊 Results:")
        print(f"   - Successfully inserted: {inserted_count} records")
        print(f"   - Duplicates skipped: {duplicate_count} records") 
        print(f"   - Pending records in DB: {pending_count}")
        print(f"   - Submitted records in DB: {submitted_count}")
        print(f"   - Total records in DB: {pending_count + submitted_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating test data: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(generate_test_data())