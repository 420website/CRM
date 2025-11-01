-- migrate:up
INSERT INTO medication_outcomes (name, is_frequent, is_default)
VALUES
  ('Active',TRUE,TRUE),
  ('Completed',TRUE,TRUE),
  ('Non Compliance',TRUE,TRUE),
  ('Side Effect',TRUE,TRUE),
  ('Tx Pending',TRUE,TRUE),
  ('Did not start',TRUE,TRUE),
  ('Death',TRUE,TRUE)
ON CONFLICT (name) DO NOTHING;

-- migrate:down
DELETE FROM medication_outcomes
WHERE name IN (
  'Active',
  'Completed',
  'Non Compliance', 
  'Side Effect',
  'Did not start',
  'Death',
  'Tx Pending'
);
