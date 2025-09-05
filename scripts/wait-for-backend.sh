#!/bin/bash

until curl -s -f "$BACKEND_URL/health" >/dev/null; do
  echo "Waiting for backend to be available @ $BACKEND_URL..."
  sleep 2
done

exec "$@"
