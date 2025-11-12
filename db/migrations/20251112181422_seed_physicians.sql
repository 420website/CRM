-- migrate:up
INSERT INTO general (name, is_frequent, is_default, type)
VALUES
  ('Dr. David Fletcher',True,True,'physician')
ON CONFLICT (name, type) DO NOTHING;


-- migrate:down
DELETE FROM general 
WHERE name IN (
  'Dr. David Fletcher'
ON CONFLICT (name, type) DO NOTHING;
);
