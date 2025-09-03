-- migrate:up
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50), 
    last_name VARCHAR(50), 
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(15),
    role TEXT NOT NULL CHECK (role IN ('admin', 'standard', 'guest')) DEFAULT 'standard' ,
    permissions TEXT[] NOT NULL DEFAULT '{}',
    password_hash VARCHAR(255) NOT NULL,
    is_verified BOOLEAN NOT NULL DEFAUlT FALSE,
    authenticator_mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ  NULL
);

CREATE TABLE IF NOT EXISTS email_mfa_codes (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    code_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS recovery_codes (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    code_hash VARCHAR(255) NOT NULL, 
    created_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE INDEX IF NOT EXISTS idx_recovery_codes_user_id ON recovery_codes (user_id);
CREATE INDEX IF NOT EXISTS idx_recovery_codes_code_hash ON recovery_codes (code_hash);

CREATE TABLE IF NOT EXISTS verification_tokens(
  id SERIAL PRIMARY KEY, 
  user_id INT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE, 
  token_hash VARCHAR(64) NOT NULL,
  token_type TEXT NOT NULL CHECK (token_type IN ('email_verification', 'password_reset')),
  expires_at TIMESTAMPTZ NOT NULL, 
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS refresh_tokens(
  id SERIAL PRIMARY KEY, 
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE, 
  token_hash VARCHAR(64) NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL, 
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- migrate:down
DROP TABLE IF EXISTS refresh_tokens;
DROP TABLE IF EXISTS verification_tokens;
DROP TABLE IF EXISTS recovery_codes;
DROP TABLE IF EXISTS email_mfa_codes;
DROP TABLE IF EXISTS users;

