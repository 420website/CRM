-- migrate:up
UPDATE patients 
SET province = 'Ontario' 
WHERE province IS NULL;

-- migrate:down
-- Cannot reverse: original NULL values are lost
