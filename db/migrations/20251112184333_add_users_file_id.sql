-- migrate:up
ALTER TABLE patients
ADD COLUMN file_id VARCHAR(20) GENERATED ALWAYS AS (
  CASE 
    WHEN first_name IS NOT NULL 
         AND last_name IS NOT NULL 
         AND dob IS NOT NULL 
         AND health_card IS NOT NULL 
    THEN 
      UPPER(SUBSTRING(first_name, 1, 1)) || 
      UPPER(SUBSTRING(last_name, 1, 1)) || 
      LPAD(EXTRACT(MONTH FROM dob)::TEXT, 2, '0') || 
      RIGHT(health_card, 2)
    ELSE NULL
  END
) STORED;

-- Force recalculation for existing rows
UPDATE patients SET id = id WHERE first_name IS NOT NULL;

-- migrate:down
ALTER TABLE patients 
DROP COLUMN file_id;

