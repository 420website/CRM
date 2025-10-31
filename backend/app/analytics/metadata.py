RELATIONSHIPS = [
    ("patients", "tests", "patient_id"),
    ("patients", "notes", "patient_id"),
    ("patients", "interactions", "patient_id"),
    ("patients", "medications", "patient_id"),
    ("patients", "dispensing", "patient_id"),
    ("patients", "activities", "patient_id"),
]

TABLE_DESCRIPTIONS = {
    "patients": (
        "Stores registration and demographic data for each patient"
        "(a.k.a. registration). Includes identifying info, contact details, "
        "test results (RNA), consent status, referral info, and timestamps. "
        "Primary key: id. Other tables link via patient_id."
    ),
    "tests": (
        "Logs individual medical test results for each patient "
        "(HIV, HCV, bloodwork). Each test row includes test type, "
        "bloowork test names are stored in bloodwork_type, these should be considered equivalent to test_type"
        "result, tester, and date."
    ),
    "notes": (
        "Contains clinician notes linked to a patient, with timestamps and template type."
    ),
    "interactions": (
        "Tracks patient interactions and payments — such as visits, outreach, "
        "or referrals — with date, description, and payment info."
    ),
    "medications": (
        "Records medications prescribed to patients, with start/end dates "
        "and outcomes."
    ),
    "dispensing": (
        "Logs dispensation events for medications (quantity, lot, expiry date, etc.)."
    ),
    "activities": (
        "Tracks planned or completed activities associated with patients "
        "(appointments, tasks, outreach)."
    ),
}

FIELD_DESCRIPTIONS = {
    "patients": {
        "id": "Primary key of the patient/registration record",
        "status": "Current registration status (e.g., pending, saved, submitted)",
        "first_name": "Patient's first name",
        "last_name": "Patient's last name",
        "dob": "Date of birth of the patient",
        "age": "Patient's age in years",
        "gender": "Gender of the patient (Male, Female)",
        "aka": "Alternate name or nickname",
        "address": "Street address",
        "unit_number": "Apartment or unit number",
        "city": "City of residence",
        "province": "Province/state of residence",
        "postal_code": "Postal or zip code",
        "phone1": "Primary contact phone",
        "phone2": "Secondary contact phone",
        "email": "Email address",
        "language": "Preferred language",
        "health_card": "Government health card number",
        "health_card_version": "Version of government health card",
        "coverage_type": "Insurance/health care coverage type",
        "disposition": "Patient status or outcome (ACTIVE, INACTIVE, etc.)",
        "physician": "Primary physician name",
        "patient_consent": "Consent type (verbal, written, etc.)",
        "leave_message": "Whether patient prefers to recieve communication via messages",
        "voicemail": "Whether pateint prefers to recieve communication via voicemail",
        "text": "Whether patient prefers to recieve communication via texts",
        "preferred_time": "Preferred contact time (morning, afternoon, evening)",
        "rna_available": "Whether RNA result is available (Yes/No)",
        "rna_sample_date": "Date RNA sample was collected",
        "rna_result": "RNA test result (Positive/Negative)",
        "referral_site": "Originating referral site",
        "referral_person": "Referral person/contact",
        "reg_date": "Registration date",
        "special_attention": "Special notes for patient care",
        "instructions": "General instructions for patient",
        "selected_template": " Name of template selected for patient (if any)",
        "summary_template": "Text body of template used",
        "finalized_at": "Timestamp when patient/registration entry was finalized",
        "created_at": "Timestamp when patient/registration entry was created",
        "updated_at": "Timestamp when patient/registration entry was last updated",
    },
    "tests": {
        "id": "Primary key for the test record",
        "patient_id": "Foreign key referencing patients.id",
        "test_type": "General type/category of test (HIV, HCV, Bloodwork, etc.)",
        "test_date": "Date the test was performed",
        "hiv_result": "Result of HIV test (positive/negative)",
        "hiv_type": "Type of HIV test",
        "hiv_tester": "Identifier of HIV tester",
        "hcv_result": "Result of HCV test",
        "hcv_tester": "Identifier of HCV tester",
        "bloodwork_type": "Type of bloodwork test (Serum, DBS, Cepheid). This field should be treated as equivalent to 'test_type' when determining the kind of test performed.",
        "bloodwork_circles": "Bloodwork circles info (if applicable)",
        "bloodwork_result": "Result of a bloodwork test",
        "bloodwork_date_submitted": "Date bloodwork was submitted",
        "bloodwork_tester": "Identifier of bloodwork tester",
        "created_at": "Timestamp record was created",
        "updated_at": "Timestamp record was updated",
    },
    "notes": {
        "id": "Primary key for the note",
        "patient_id": "Foreign key referencing patients.id",
        "template_type": "Type of template used for note",
        "note_date": "Date of note entry",
        "note_text": "Full text of the note",
        "created_at": "Timestamp note was created",
        "updated_at": "Timestamp note was updated",
    },
    "interactions": {
        "id": "Primary key for the interaction",
        "patient_id": "Foreign key referencing patients.id",
        "date": "Date that the interaction occured on",
        "description": "Textual description of the interaction, details of what happened.",
        "referral_id": "If the description is a referral this will contain the referral id",
        "amount": "If there is a reward or amount of money related to the transaction this is the dollar value",
        "payment_type": "If an exchange of money related to transaction this holds the way in which it was paid",
        "issued": "If it was paid or not",
        "note_date": "Date of note entry",
        "note_text": "Full text of the note",
        "created_at": "Timestamp interaction entry was created",
        "updated_at": "Timestamp interaction entry was updated",
    },
    "medications": {
        "id": "Primary key for the medication",
        "patient_id": "Foreign key referencing patients.id",
        "medication": "Name of the medication",
        "start_date": "Date the medication is to be started this could potentially be NULL",
        "end_date": "Date the medication is expected to be finished this could potentially be NULL",
        "outcome": "Result of the medication e.g., Active, Completed, Side Effect, Did not start, Death",
        "created_at": "Timestamp medication entry was created",
        "updated_at": "Timestamp medication entry was updated",
    },
    "dispensing": {
        "id": "Primary key for the dispensing",
        "patient_id": "Foreign key referencing patients.id",
        "medication": "Name of the medication being dispensed",
        "rx": "The Rx number assigned to the medication",
        "quantity": "The number of doses to be dispensed",
        "lot": "The lot number assigned to the medication being dispensed",
        "product_type": "Type of dispensing options are either Commercial or Compassion",
        "expiry_date": "Date the dispensed medication expires",
        "created_at": "Timestamp dispensing entry was created",
        "updated_at": "Timestamp dispensing entry was updated",
    },
    "activities": {
        "id": "Primary key for the activity",
        "patient_id": "Foreign key referencing patients.id",
        "date": "Date the activity is to occur",
        "time": "Time at which the activity is to occur",
        "description": "Textual description of the activity",
        "completed": "Whether the activity has been completed or not",
        "created_at": "Timestamp activity entry was created",
        "updated_at": "Timestamp activity entry was updated",
    },
}
