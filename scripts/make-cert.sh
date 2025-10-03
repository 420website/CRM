#!/bin/bash

### This is used to create certs for local development only. Run prior to running in dev ###

mkdir -p ./certs

# Check mkcert exists
if ! command -v mkcert &>/dev/null; then
  echo "'mkcert' not available"
  exit 1
fi

# Generate CA and server certificates
mkcert -cert-file ./certs/server.crt -key-file ./certs/server.key postgres_dev localhost minio 127.0.0.1
cp "$(mkcert -CAROOT)/rootCA.pem" ./certs/ca.crt

# Set proper permissions
chown 999:999 ./certs/server.key ./certs/server.crt ./certs/ca.crt
chmod 600 ./certs/server.key
chmod 644 ./certs/server.crt ./certs/ca.crt
