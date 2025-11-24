-- migrate:up
INSERT INTO reference_options (name,type,is_frequent,is_default)
VALUES
  ('HIV','assessment_type',TRUE,TRUE),
  ('HCV','assessment_type',TRUE,TRUE),
  ('Bloodwork','assessment_type',TRUE,TRUE),
  ('Positive','assessment_result',TRUE,TRUE),
  ('Negative','assessment_result',TRUE,TRUE),
  ('Pending','assessment_result',TRUE,TRUE),
  ('Error','assessment_result',TRUE,TRUE),
  ('JY','assessment_tester',TRUE,TRUE),
  ('CM','assessment_tester',TRUE,TRUE)
ON CONFLICT (name, type) DO NOTHING;

-- migrate:down
DELETE FROM reference_options
WHERE (name, type) IN (
  ('HIV', 'assessment_type'),
  ('HCV', 'assessment_type'),
  ('Bloodwork', 'assessment_type'),
  ('Positive','assessment_result'),
  ('Negative','assessment_result'),
  ('Pending','assessment_result'),
  ('Error','assessment_result'),
  ('JY','assessment_tester'),
  ('CM','assessment_tester')
);

