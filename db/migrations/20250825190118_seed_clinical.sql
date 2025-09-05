-- migrate:up
INSERT INTO clinical_templates (name, content, is_default)
VALUES
  ('Positive',
   'Dx 10+ years ago and treated. RNA - no labs available. However, has had ongoing risk factors with sharing pipes and straws. Counselled regarding risk factors. Point of care test was completed for HCV and tested positive at approximately two minutes with a dark line. HIV testing came back negative. Collected a DBS specimen and advised that it will take approximately 7 to 10 days for results. Referral: none. Client does have a valid address and has also provided a phone number for results.',
   TRUE
  ),
  ('Negative - Pipes',
   '',
   TRUE
  ),
  ('Negative - Pipes/Straws',
   '',
   TRUE
  ),
  ('Negative - Pipes/Straws/Needles',
   '',
   TRUE
  )
ON CONFLICT (name) DO NOTHING;

-- migrate:down
DELETE FROM clinical_templates
WHERE name IN (
  'Positive',
  'Negative - Pipes',
  'Negative - Pipes/Straws',
  'Negative - Pipes/Straws/Needles'
);

