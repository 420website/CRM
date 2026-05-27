-- migrate:up
ALTER TABLE users
ADD COLUMN location_permissions TEXT[] NOT NULL DEFAULT '{}';

ALTER TABLE users
ADD COLUMN province VARCHAR(100) DEFAULT 'Ontario';

UPDATE users 
SET province = 'Ontario';

UPDATE users 
SET location_permissions = '{All}';

-- migrate:down
ALTER TABLE users 
DROP COLUMN province;

ALTER TABLE users 
DROP COLUMN location_permissions;

