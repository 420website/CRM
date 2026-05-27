-- migrate:up
ALTER TABLE activities 
ADD COLUMN name VARCHAR(50) NOT NULL DEFAULT 'General Activity';

-- migrate:down
ALTER TABLE activities 
DROP column name;



