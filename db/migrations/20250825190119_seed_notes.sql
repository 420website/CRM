-- migrate:up
INSERT INTO note_templates (name, content, is_default)
VALUES
  ('Consultation',
   '',
   TRUE
  ),
  ('Lab',
   '',
   TRUE
  ),
  ('Prescription',
   '',
   TRUE
  )
ON CONFLICT (name) DO NOTHING;

-- migrate:down
DELETE FROM note_templates
WHERE name IN (
  'Consultation',
  'Lab',
  'Prescription'
);
