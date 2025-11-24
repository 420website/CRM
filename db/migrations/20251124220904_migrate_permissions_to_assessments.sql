-- migrate:up
UPDATE users 
SET permissions = array_replace(permissions, 'tests', 'assessments')
WHERE 'tests' = ANY(permissions);

-- migrate:down
UPDATE users 
SET permissions = array_replace(permissions, 'assessments', 'tests')
WHERE 'assessments' = ANY(permissions);
