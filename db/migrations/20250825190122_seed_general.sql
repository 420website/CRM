-- migrate:up
INSERT INTO general (name, is_frequent, is_default, type)
VALUES
  ('Screening',True,True,'interaction'),
  ('Adherence',True,True,'interaction'),
  ('Bloodwork',True,True,'interaction'),
  ('Discretionary',True,True,'interaction'),
  ('Referral',True,True,'interaction'),
  ('Consultation',True,True,'interaction'),
  ('Outreach',True,True,'interaction'),
  ('Repeat',True,True,'interaction'),
  ('Results',True,True,'interaction'),
  ('Safe Supply',True,True,'interaction'),
  ('Lab Req',True,True,'interaction'),
  ('Telephone',True,True,'interaction'),
  ('Remittance',True,True,'interaction'),
  ('Update',True,True,'interaction'),
  ('Counselling',True,True,'interaction'),
  ('Trillium',True,True,'interaction'),
  ('Housing',True,True,'interaction'),
  ('SOT',True,True,'interaction'),
  ('EOT',True,True,'interaction'),
  ('SVR',True,True,'interaction'),
  ('Locate',True,True,'interaction'),
  ('Staff',True,True,'interaction'),
  ('Staff',True,True,'interaction'),
  ('Staff',True,True,'interaction'),
  ('Staff',True,True,'interaction'),
  ('Staff',True,True,'interaction'),
  ('OW',True,True,'coverage'),
  ('ODSP',True,True,'coverage'),
  ('No Coverage',True,True,'coverage')
ON CONFLICT (name) DO NOTHING;

-- migrate:down
DELETE FROM general 
WHERE name IN (
  'Screening',
  'Adherence',
  'Bloodwork',
  'Discretionary',
  'Referral',
  'Consultation',
  'Outreach',
  'Repeat',
  'Results',
  'Safe Supply',
  'Lab Req',
  'Telephone',
  'Remittance',
  'Update',
  'Counselling',
  'Trillium',
  'Housing',
  'SOT',
  'EOT',
  'SVR',
  'Locate',
  'Staff',
  'OW',
  'ODSP',
  'No Coverage'
ON CONFLICT (name) DO NOTHING;
);
