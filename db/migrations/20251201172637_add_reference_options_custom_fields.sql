-- migrate:up
ALTER TABLE reference_options 
ADD COLUMN IF NOT EXISTS custom_fields JSONB DEFAULT '{}'::jsonb;

ALTER TABLE reference_options 
DROP CONSTRAINT IF EXISTS reference_options_name_type_key;

ALTER TABLE reference_options 
ADD CONSTRAINT reference_options_name_type_custom_fields UNIQUE(name, type, custom_fields);

UPDATE reference_options
SET custom_fields = jsonb_build_object('province', 'Ontario')
WHERE type = 'referral_site';

-- migrate:down
ALTER TABLE reference_options 
DROP CONSTRAINT IF EXISTS reference_options_name_type_custom_fields;

ALTER TABLE reference_options 
ADD CONSTRAINT reference_options_name_type_key UNIQUE(name, type);

ALTER TABLE reference_options 
DROP COLUMN custom_fields;

