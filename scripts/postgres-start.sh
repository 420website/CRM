#!/bin/bash

# Copy the key to a writable location and fix ownership
cp /certs/server.key /tmp/server.key
chown postgres:postgres /tmp/server.key
chmod 600 /tmp/server.key

exec docker-entrypoint.sh postgres \
  -c ssl=on \
  -c ssl_cert_file=/certs/server.crt \
  -c ssl_key_file=/tmp/server.key \
  -c ssl_ca_file=/certs/ca-chain.crt \
  -c ssl_min_protocol_version=TLSv1.2 \
  -c logging_collector=on \
  -c log_directory='log' \
  -c log_filename='postgresql.log' \
  -c log_statement='mod' \
  -c log_destination='csvlog,stderr' \
  -c log_min_messages=info \
  -c log_rotation_age=0 \
  -c log_rotation_size=0 \
  -c log_truncate_on_rotation=off \
  -c app.legacy_instance=${IS_MY420:-false}
