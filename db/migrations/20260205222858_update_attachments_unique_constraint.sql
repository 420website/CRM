-- migrate:up
ALTER TABLE attachments 
DROP CONSTRAINT attachments_patient_id_file_name_key;

ALTER TABLE attachments 
ADD CONSTRAINT attachments_file_key_key UNIQUE (file_key);

-- migrate:down

