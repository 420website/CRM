-- migrate:up

-- Create new consolidated tables
CREATE TABLE reference_options (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'disposition', 'document_type'
    is_frequent BOOLEAN DEFAULT false,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (name, type)
);

CREATE TABLE reference_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'note', 'clinical', 'medication'
    content TEXT NOT NULL,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (name, type)
);

-- Migrate data from old tables to reference_options
INSERT INTO reference_options (name, type, is_frequent, is_default, created_at, updated_at)
SELECT name, 'disposition', is_frequent, is_default, created_at, updated_at FROM dispositions;

INSERT INTO reference_options (name, type, is_frequent, is_default, created_at, updated_at)
SELECT name, 'document_type', is_frequent, is_default, created_at, updated_at FROM document_types;

INSERT INTO reference_options (name, type, is_frequent, is_default, created_at, updated_at)
SELECT name, 'referral_site', is_frequent, is_default, created_at, updated_at FROM referral_sites;

INSERT INTO reference_options (name, type, is_frequent, is_default, created_at, updated_at)
SELECT name, 'medication_outcome', is_frequent, is_default, created_at, updated_at FROM medication_outcomes;

INSERT INTO reference_options (name, type, is_frequent, is_default, created_at, updated_at)
SELECT name, 'medication', is_frequent, is_default, created_at, updated_at FROM medication_templates;

INSERT INTO reference_options (name, type, is_frequent, is_default, created_at, updated_at)
SELECT name, type, is_frequent, is_default, created_at, updated_at FROM general;

-- Migrate data from old tables to reference_templates
INSERT INTO reference_templates (name, type, content, is_default, created_at, updated_at)
SELECT name, 'note', content, is_default, created_at, updated_at FROM note_templates;

INSERT INTO reference_templates (name, type, content, is_default, created_at, updated_at)
SELECT name, 'clinical', content, is_default, created_at, updated_at FROM clinical_templates;


-- Drop old tables
-- DROP TABLE IF EXISTS note_templates;
-- DROP TABLE IF EXISTS clinical_templates;
-- DROP TABLE IF EXISTS dispositions;
-- DROP TABLE IF EXISTS document_types;
-- DROP TABLE IF EXISTS referral_sites;
-- DROP TABLE IF EXISTS medication_templates;
-- DROP TABLE IF EXISTS medication_outcomes;
-- DROP TABLE IF EXISTS general;

-- migrate:down
-- CREATE TABLE IF NOT EXISTS note_templates (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(200) NOT NULL UNIQUE,
--     content TEXT NOT NULL,
--     is_default BOOLEAN DEFAULT false,
--     created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
-- );
--
-- INSERT INTO note_templates (name, content, is_default, created_at, updated_at)
-- SELECT name, content, is_default, created_at, updated_at FROM reference_templates;
--
-- CREATE TABLE clinical_templates (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(200) NOT NULL UNIQUE,
--     content TEXT NOT NULL,
--     is_default BOOLEAN DEFAULT false,
--     created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
-- );
--
-- INSERT INTO clinical_templates (name, content, is_default, created_at, updated_at)
-- SELECT name, content, is_default, created_at, updated_at FROM reference_templates;
--
-- CREATE TABLE dispositions (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(200) NOT NULL UNIQUE,
--     is_frequent BOOLEAN DEFAULT false,
--     is_default BOOLEAN DEFAULT false,
--     created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
-- );
--
-- INSERT INTO dispositions (name, is_frequent, is_default, created_at, updated_at)
-- SELECT name, is_frequent, is_default, created_at, updated_at FROM reference_options;
--
-- CREATE TABLE document_types (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(200) NOT NULL UNIQUE,
--     is_default BOOLEAN DEFAULT false,
--     is_frequent BOOLEAN DEFAULT false,
--     created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
-- );
--
-- INSERT INTO document_types (name, is_frequent, is_default, created_at, updated_at)
-- SELECT name, is_frequent, is_default, created_at, updated_at FROM reference_options;
--
-- CREATE TABLE referral_sites (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(200) NOT NULL UNIQUE,
--     is_frequent BOOLEAN DEFAULT false,
--     is_default BOOLEAN DEFAULT false,
--     created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
-- );
--
-- INSERT INTO referral_sites (name, is_frequent, is_default, created_at, updated_at)
-- SELECT name, is_frequent, is_default, created_at, updated_at FROM reference_options;
--
-- CREATE TABLE medication_templates (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(200) NOT NULL UNIQUE,
--     is_frequent BOOLEAN DEFAULT false,
--     is_default BOOLEAN DEFAULT false,
--     created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
-- );
--
-- INSERT INTO medication_templates (name, is_frequent, is_default, created_at, updated_at)
-- SELECT name, is_frequent, is_default, created_at, updated_at FROM reference_options;
--
-- CREATE TABLE medication_outcomes (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(200) NOT NULL UNIQUE,
--     is_frequent BOOLEAN DEFAULT false,
--     is_default BOOLEAN DEFAULT false,
--     created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
-- );
--
-- INSERT INTO medication_outcomes (name, content, is_default, created_at, updated_at)
-- SELECT name, is_default, created_at, updated_at FROM reference_options;
--
-- CREATE TABLE general (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(200) NOT NULL,
--     is_frequent BOOLEAN DEFAULT false,
--     is_default BOOLEAN DEFAULT false,
--     type VARCHAR(50) NOT NULL DEFAULT 'unknown', 
--     created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
--     UNIQUE (name, type)
-- );
--
-- INSERT INTO reference_options (name, type, is_frequent, is_default, created_at, updated_at)
-- SELECT name, type, is_frequent, is_default, created_at, updated_at FROM general;

-- Drop new tables
DROP TABLE IF EXISTS reference_options;
DROP TABLE IF EXISTS reference_templates;
