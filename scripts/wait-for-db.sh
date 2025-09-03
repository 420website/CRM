#!/bin/bash
set -e

echo "Waiting for PostgreSQL at $PSQL_HOST:$PSQL_PORT..."

# Wait for PostgreSQL to be available
until pg_isready -h "$PSQL_HOST" -p "$PSQL_PORT" -U "$PSQL_USER" -d "$PSQL_DATABASE"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up. Starting backend..."
exec "$@"
