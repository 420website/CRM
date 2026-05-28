-- migrate:up
ALTER TABLE patients DROP COLUMN age;

-- ALTER TABLE patients 
--   ADD COLUMN age INT GENERATED ALWAYS AS (DATE_PART('year', AGE(dob))) STORED;

-- migrate:down
ALTER TABLE patients ADD COLUMN age INT;
-- ALTER TABLE patients DROP COLUMN age;

