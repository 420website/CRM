RELATIONSHIPS = [
    ("patients", "assessments", "patient_id"),
    ("patients", "notes", "patient_id"),
    ("patients", "interactions", "patient_id"),
    ("patients", "medications", "patient_id"),
    ("patients", "dispensing", "patient_id"),
    ("patients", "activities", "patient_id"),
    ("patients", "acttachments", "patient_id"),
    ("patients", "patient_photos", "patient_id"),
]

TABLE_DESCRIPTIONS = {
    "patients": (
        "Stores registration and demographic data for each patient"
        "(a.k.a. registration, client). Includes identifying info, contact details, "
        "test results (RNA), consent status, referral info, and timestamps. "
        "Primary key: id. Other tables link via patient_id."
    ),
    "patient_photos": (
        "Stores patient profile photos. Each record links a photo to a patient "
        "via patient_id. Contains the original filename (photo_name) and the "
        "unique storage key (photo_key) used to retrieve the image from object storage. "
        "Tracks when each photo was uploaded (uploaded_at)."
    ),
    "attachments": (
        "Stores document attachments for patients such as medical records, insurance cards, "
        "ID documents, and consent forms. Each record links to a patient via patient_id. "
        "Contains the original filename (file_name), unique storage key (file_key), "
        "file metadata (file_size, mime_type), document category (document_type), "
        "and upload timestamp (uploaded_at)."
    ),
    "assessments": (
        "Logs individual medical assessement results for each patient "
        "(a.k.as tests, test)"
        "(HIV, HCV, bloodwork). Each row includes type, result, tester, date and data"
        "data is a json object contain information specfic to each assessment, it can potential be null or and empyty object"
        "bloodwork test names are stored in data.bloodwork_type, these should be considered equivalent to type"
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
    "reference_options": (
        "Stores user-configurable dropdown options used throughout the system. "
        "Supports different option types (e.g., 'disposition', 'document_type') that populate "
        "dropdowns and selection fields. Each option can be marked as frequently used (is_frequent). "
        "Not directly linked to other tables via foreign keys, but "
        "values are referenced in fields like attachments.document_type, interactions disposition, etc."
    ),
    "reference_templates": (
        "Stores reusable templates that users can apply when creating content. "
        "Supports different template types (e.g., 'note', 'clinical', 'medication') with "
        "pre-written content that can be used as starting points. For example, note templates "
        "provide pre-filled text when clinicians add notes to patients, saving time and ensuring "
        "consistency.Not directly linked via foreign keys, but referenced when users select templates during data entry."
    ),
}

FIELD_DESCRIPTIONS = {
    "patients": {
        "id": "Primary key of the patient/registration record",
        "status": "Current registration status (e.g., pending, saved, submitted)",
        "first_name": "Patient's first name",
        "last_name": "Patient's last name",
        "dob": "Date of birth of the patient",
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
        "finalized_at": "Timestamp when client/patient/registration entry was finalized",
        "created_at": "Timestamp when client/patient/registration entry was created",
        "updated_at": "Timestamp when client/patient/registration entry was last updated",
    },
    "patient_photos": {
        "id": "Primary key for the patient photo record",
        "patient_id": "Foreign key referencing patients.id - links the photo to a specific patient",
        "photo_name": "Original filename of the uploaded patient photo (e.g., 'john_doe_headshot.jpg')",
        "photo_key": "Unique storage key/path used to retrieve the photo from object storage (e.g., S3 bucket key)",
        "uploaded_at": "Timestamp indicating when the photo was uploaded to the system",
    },
    "attachments": {
        "id": "Primary key for the patient attachment record",
        "patient_id": "Foreign key referencing patients.id - links the attachment to a specific patient",
        "file_name": "Original filename of the uploaded document (e.g., 'medical_report.pdf', 'insurance_card.jpg')",
        "file_key": "Unique storage key/path used to retrieve the file from object storage (e.g., S3 bucket key)",
        "file_size": "Size of the uploaded file in bytes",
        "mime_type": "MIME type of the file indicating its format (e.g., 'application/pdf', 'image/jpeg', 'image/png')",
        "document_type": "Category or type of document (e.g., 'Medical Record', 'Insurance Card', 'ID Document', 'Consent Form')",
        "uploaded_at": "Timestamp indicating when the attachment was uploaded to the system",
    },
    "assessments": {
        "id": "Primary key for the test record",
        "patient_id": "Foreign key referencing patients.id",
        "type": "General type/category of test (HIV, HCV, Bloodwork, etc.)",
        "date": "Date the test was performed",
        "result": "Result of assessment (Positive, Negative,etc.)",
        "tester": "Identifier of assessment tester",
        "data": "Json object containing specific information to each test type, this can vary by assessment, may be best to query all together an examine after",
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
    "reference_options": {
        "id": "Primary key for the reference option record",
        "name": "The display name/value of the option that appears in dropdown menus or selection fields (e.g., 'Insurance Card', 'Follow-up Visit', 'Reactive')",
        "type": "Category that groups related options together - determines where the option appears (e.g., 'document_type' for attachment categories, 'disposition' for patient status, 'test' for test types, 'medication' for drug names, 'dispensing_quantity' for dosage amounts)",
        "is_frequent": "Boolean flag that marks this option as frequently used - tenant-configurable to highlight commonly selected options in the UI",
        "created_at": "Timestamp when the option was created",
        "updated_at": "Timestamp when the option was last modified",
    },
    "reference_templates": {
        "id": "Primary key for the reference template record",
        "name": "The display name of the template that appears in dropdown/selection menus when users choose a template to apply (e.g., 'Initial Assessment', 'Follow-up Note', 'Medication Plan')",
        "type": "Category that groups related templates together - determines the context where templates are used (e.g., 'note' for clinical notes, 'clinical' for clinical assessments, 'medication' for prescription templates)",
        "content": "The pre-written text body of the template that gets inserted when a user selects this template - serves as a starting point that can be edited",
        "created_at": "Timestamp when the template was created",
        "updated_at": "Timestamp when the template was last modified",
    },
}
