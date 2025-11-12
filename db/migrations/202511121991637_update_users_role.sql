-- migrate:up
ALTER TABLE users 
DROP CONSTRAINT IF EXISTS users_role_check;

ALTER TABLE users 
ALTER COLUMN role SET DEFAULT 'standard';

-- migrate:down
ALTER TABLE users 
ADD CONSTRAINT users_role_check CHECK (role IN ('admin', 'standard', 'guest'));
ALTER TABLE users 
ALTER COLUMN role SET DEFAULT 'standard';
