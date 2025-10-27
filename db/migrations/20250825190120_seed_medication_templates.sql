-- migrate:up
INSERT INTO medication_templates (name, is_frequent, is_default)
VALUES
  ('Epclusa',TRUE,TRUE),
  ('Maviret',TRUE,TRUE),
  ('Vosevi',TRUE,TRUE)
ON CONFLICT (name) DO NOTHING;

-- migrate:down
DELETE FROM medication_templates
WHERE name IN (
  'Epclusa',
  'Maviret',
  'Vosevi'
);
