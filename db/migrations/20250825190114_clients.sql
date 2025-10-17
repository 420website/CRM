-- migrate:up
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    age INT,                               
    gender VARCHAR(20),
    aka VARCHAR(100),                       
    address TEXT,
    unit_number VARCHAR(20),
    city VARCHAR(100),
    province VARCHAR(100),
    postal_code VARCHAR(20),
    phone1 VARCHAR(20),
    phone2 VARCHAR(20),
    email VARCHAR(150),
    language VARCHAR(20),

    -- Health info
    health_card VARCHAR(20) ,
    health_card_version VARCHAR(5),
    coverage_type VARCHAR(50),
    disposition VARCHAR(50),                -- ACTIVE, INACTIVE, etc.
    physician VARCHAR(150),

    -- Consent / communication
    patient_consent VARCHAR(50),            -- verbal, written, etc.
    leave_message BOOLEAN DEFAULT false,
    voicemail BOOLEAN DEFAULT false,
    text BOOLEAN DEFAULT false,
    preferred_time VARCHAR(50),             -- morning, afternoon, evening

    -- Test results
    hiv_date DATE,
    hiv_result VARCHAR(50),                 -- positive / negative
    hiv_tester VARCHAR(50),
    hiv_type VARCHAR(50),
    rna_available VARCHAR(20),              -- Yes/No
    rna_result VARCHAR(50),                 -- Positive/Negative
    rna_sample_date DATE,

    -- Referral / registration
    referral_site VARCHAR(200),
    referral_person VARCHAR(150),
    reg_date DATE DEFAULT CURRENT_DATE,

    -- Notes / misc
    special_attention TEXT,
    instructions TEXT,
    selected_template VARCHAR(200),         -- foreign key if linking to templates
    summary_template TEXT,
    test_type VARCHAR(50),                  -- e.g. "Tests"
    -- photo TEXT,                             -- base64 or URL

    -- Timestamps
    finalized_at TIMESTAMPTZ DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Prevent duplicate health cards except when it's '000000'
CREATE UNIQUE INDEX unique_health_card
    ON patients (health_card)
    WHERE health_card <> '0000000000';

-- Table tracks metadata for photos stored in object storage
CREATE TABLE IF NOT EXISTS patient_photos (
  id SERIAL PRIMARY KEY,
  patient_id INTEGER NOT NULL UNIQUE REFERENCES patients(id) ON DELETE CASCADE,
  photo_name VARCHAR(100) NOT NULL,
  photo_key VARCHAR(200) NOT NULL,
  -- mime_type VARCHAR(100),
  uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS attachments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_key VARCHAR(500) NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    document_type VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (patient_id , file_name)
);

-- Create test_results table that references the patients table
CREATE TABLE tests (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    test_type VARCHAR(100),
    test_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- HIV Testing
    hiv_result VARCHAR(20) DEFAULT 'negative',
    hiv_type VARCHAR(50),
    hiv_tester VARCHAR(10) DEFAULT 'CM',
    
    -- HCV Testing
    hcv_result VARCHAR(20) DEFAULT 'negative',
    hcv_tester VARCHAR(10) DEFAULT 'CM',
    
    -- Bloodwork Testing
    bloodwork_type VARCHAR(100),
    bloodwork_circles VARCHAR(100),
    bloodwork_result VARCHAR(20) DEFAULT 'Pending',
    bloodwork_date_submitted DATE,
    bloodwork_tester VARCHAR(10) DEFAULT 'CM',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create notes table that references the patients table
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    template_type VARCHAR(50) NOT NULL,
    note_date DATE NOT NULL DEFAULT CURRENT_DATE,
    note_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create interactions table that references the patients table
CREATE TABLE interactions (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    description TEXT,
    referral_id VARCHAR(100),
    amount DECIMAL(10, 2),
    payment_type VARCHAR(50),
    issued VARCHAR(50) DEFAULT 'Select',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create medications table that references the patients table
CREATE TABLE medications (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    medication VARCHAR(255) NOT NULL,
    start_date DATE,
    end_date DATE,
    outcome TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create dispensing table that references the patients table
CREATE TABLE dispensing (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    medication VARCHAR(255) NOT NULL,
    rx VARCHAR(100),
    quantity INTEGER DEFAULT 28,
    lot VARCHAR(100),
    product_type VARCHAR(50) DEFAULT 'Commercial',
    expiry_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create activities table that references the patients table
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    time TIME,
    description TEXT NOT NULL,
    completed bool NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);


-- migrate:down
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS patient_photos;
DROP TABLE IF EXISTS tests;
DROP TABLE IF EXISTS notes;
DROP TABLE IF EXISTS attachments;
DROP TABLE IF EXISTS interactions;
DROP TABLE IF EXISTS medications;
DROP TABLE IF EXISTS dispensing;
DROP TABLE IF EXISTS activities;
