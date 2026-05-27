-- migrate:up
DO $$
BEGIN
  IF current_setting('app.legacy_instance', true) = 'false' THEN
    DELETE FROM reference_options WHERE is_default=True;
    DELETE FROM reference_templates WHERE is_default=True; 
  END IF;
END $$;

-- migrate:down

