-- migrate:up
CREATE TABLE IF NOT EXISTS assessments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    type VARCHAR(250), 
    date DATE NOT NULL DEFAULT CURRENT_DATE, 
    result VARCHAR(100), 
    tester VARCHAR(100),
    data JSON,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Migrate HCV tests
INSERT INTO assessments (patient_id, type, date, result, tester, data, created_at, updated_at)
SELECT 
    patient_id, 
    'HCV' as type, 
    test_date, 
    hcv_result, 
    hcv_tester,
    NULL as data,
    created_at, 
    updated_at 
FROM tests
WHERE hcv_result IS NOT NULL;

-- Migrate HIV tests
INSERT INTO assessments (patient_id, type, date, result, tester, data, created_at, updated_at)
SELECT 
    patient_id, 
    'HIV' as type, 
    test_date, 
    hiv_result, 
    hiv_tester,
    jsonb_build_object('hiv_type', hiv_type) as data,
    created_at, 
    updated_at 
FROM tests
WHERE hiv_result IS NOT NULL;

-- Migrate Bloodwork tests
INSERT INTO assessments (patient_id, type, date, result, tester, data, created_at, updated_at)
SELECT 
    patient_id, 
    'Bloodwork' as type, 
    test_date, 
    bloodwork_result, 
    bloodwork_tester,
    jsonb_build_object(
        'bloodwork_type', bloodwork_type,
        'bloodwork_circles', bloodwork_circles,
        'bloodwork_date_submitted', bloodwork_date_submitted
    ) as data,
    created_at, 
    updated_at 
FROM tests
WHERE bloodwork_type IS NOT NULL;

UPDATE assessments
SET result = INITCAP(result);

-- migrate:down
DROP TABLE IF EXISTS assessments;

