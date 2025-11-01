-- migrate:up
INSERT INTO document_types (name, is_frequent, is_default)
VALUES
  ('Consultation Report', TRUE, TRUE),
  ('Treatment Consent', TRUE, TRUE),
  ('HCV Perscription', TRUE, TRUE)
ON CONFLICT (name) DO NOTHING;

-- migrate:down
DELETE FROM document_types
WHERE name IN (
  'Consultation Report',
  'Treatment Consent',
  'HCV Perscription',
);

