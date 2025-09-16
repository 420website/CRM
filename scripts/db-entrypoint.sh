#! /bin/bash

set -e

DATA_DIR=/var/lib/postgresql/data

# Generate SSL cert if missing
if [ ! -f "$DATA_DIR/server.key" ]; then
  echo "Generating self-signed SSL certificate..."
  openssl req -new -x509 -days 365 -nodes -text \
    -out "$DATA_DIR/server.crt" \
    -keyout "$DATA_DIR/server.key" \
    -subj "/CN=postgres"
  chown postgres:postgres "$DATA_DIR"/server.*
  chmod 600 "$DATA_DIR/server.key"
  chmod 644 "$DATA_DIR/server.crt"
fi

# Start Postgres
exec postgres -c ssl=on \
  -c ssl_cert_file="$DATA_DIR/server.crt" \
  -c ssl_key_file="$DATA_DIR/server.key"
