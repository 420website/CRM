-- migrate:up
INSERT INTO referral_sites (name, is_frequent, is_default)
VALUES
  -- Most frequently used referral sites
  ('Toronto - Outreach', TRUE, TRUE),
  ('Hamilton - Wellington', TRUE, TRUE),
  ('London - LMP', TRUE, TRUE),
  ('Ottawa - Outreach', TRUE, TRUE),
  ('Windsor - Outreach', TRUE, TRUE),

  -- All other referral sites in alphabetical order
  ('Barrie - City Centre Pharmacy', FALSE, TRUE),
  ('Barrie - John Howard Society of Sir', FALSE, TRUE),
  ('Brantford - Outreach', FALSE, TRUE),
  ('Hamilton - Homewood Suit', FALSE, TRUE),
  ('Kingston - Outreach', FALSE, TRUE),
  ('London - LMP (Night)', FALSE, TRUE),
  ('Niagara - Community Health', FALSE, TRUE),
  ('Niagara - Crysler House', FALSE, TRUE),
  ('Niagara - Summer', FALSE, TRUE),
  ('Orillia - Downtown Dispensary', FALSE, TRUE),
  ('Orillia - John Howard Society', FALSE, TRUE),
  ('Orillia - The Light House', FALSE, TRUE),
  ('Toronto - Dixon Hall (Lakeshore)', FALSE, TRUE),
  ('Toronto - Margaret''s Drop-In', FALSE, TRUE),
  ('Toronto - Renascent (Dundas)', FALSE, TRUE),
  ('Toronto - Renascent (Whitby)', FALSE, TRUE),
  ('Toronto - St. Felix Centre', FALSE, TRUE),
  ('Windsor - Downtown Mission', FALSE, TRUE),
  ('Windsor - Night', FALSE, TRUE),
  ('Windsor - Salvation Army', FALSE, TRUE)
ON CONFLICT (name) DO NOTHING;

-- migrate:down
DELETE FROM referral_sites
WHERE name IN (
  'Toronto - Outreach',
  'Hamilton - Wellington',
  'London - LMP',
  'Ottawa - Outreach',
  'Windsor - Outreach',

  'Barrie - City Centre Pharmacy',
  'Barrie - John Howard Society of Sir',
  'Brantford - Outreach',
  'Hamilton - Homewood Suit',
  'Kingston - Outreach',
  'London - LMP (Night)',
  'Niagara - Community Health',
  'Niagara - Crysler House',
  'Niagara - Summer',
  'Orillia - Downtown Dispensary',
  'Orillia - John Howard Society',
  'Orillia - The Light House',
  'Toronto - Dixon Hall (Lakeshore)',
  'Toronto - Margaret''s Drop-In',
  'Toronto - Renascent (Dundas)',
  'Toronto - Renascent (Whitby)',
  'Toronto - St. Felix Centre',
  'Windsor - Downtown Mission',
  'Windsor - Night',
  'Windsor - Salvation Army'
);

