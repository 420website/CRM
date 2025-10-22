-- migrate:up
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  -- only update if column exists (safe for tables without updated_at)
  IF (NEW.* IS DISTINCT FROM OLD.*) THEN
    NEW.updated_at = NOW();
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- migrate:down
DROP FUNCTION IF EXISTS set_updated_at() CASCADE;


