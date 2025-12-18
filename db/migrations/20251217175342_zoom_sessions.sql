-- migrate:up
CREATE TABLE IF NOT EXISTS zoom_session (
  id SERIAL PRIMARY KEY,
  patient_id INT UNIQUE  NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
  session_name VARCHAR(250) NOT NULL, 
  session_key VARCHAR(250) NOT NULL, 
  host_id INT NOT NULL, 
  is_locked BOOL DEFAULT FALSE, 
  locked_at TIMESTAMPTZ, 
  is_deleted BOOL DEFAULT FALSE,
  deleted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ
    -- config = Column(JSON)  # Store any extra Zoom config

);
CREATE INDEX IF NOT EXISTS idx_zoom_session_patient_id ON zoom_session (patient_id);

-- migrate:down
DROP INDEX IF EXISTS idx_zoom_session_patient_id;
DROP TABLE IF EXISTS zoom_session;

