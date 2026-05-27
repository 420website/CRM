-- migrate:up
ALTER TABLE IF EXISTS reference_options 
DROP COLUMN IF EXISTS is_default;

ALTER TABLE IF EXISTS reference_templates 
DROP COLUMN IF EXISTS is_default;

-- migrate:down
-- Cannot reverse: original values are lost
