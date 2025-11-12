-- migrate:up
ALTER TABLE patients 
ADD COLUMN limited BOOLEAN  NOT NULL DEFAULT TRUE;


-- migrate:down
ALTER TABLE patients 
DROP column limited;

