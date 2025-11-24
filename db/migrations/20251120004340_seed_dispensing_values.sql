-- migrate:up
INSERT INTO reference_options (name, type, is_frequent, is_default)
VALUES
  ('14','dispensing_quantity',TRUE,TRUE),
  ('28','dispensing_quantity',TRUE,TRUE),
  ('56','dispensing_quantity',TRUE,TRUE),
  ('84','dispensing_quantity',TRUE,TRUE),
  ('Commercial','dispensing_type',TRUE,TRUE),
  ('Compassionate','dispensing_type',TRUE,TRUE)
ON CONFLICT (name, type) DO NOTHING;

-- migrate:down
DELETE FROM reference_options
WHERE name IN (
  ('14','dispensing_quantity'),
  ('28','dispensing_quantity'),
  ('56','dispensing_quantity'),
  ('84','dispensing_quantity'),
  ('Commercial','dispensing_type'),
  ('Compassionate','dispensing_type')
);

