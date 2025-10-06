#!/bin/bash

# Remove trigger if it exists
rm -f /etc/vault/.cert-trigger

while true; do
  inotifywait -e create /etc/vault/.cert-trigger 2>/dev/null
  rm -f /etc/vault/.cert-trigger
  echo "$(date) - Detected trigger, restarting cert-dependent containers"
  docker compose --profile cert-reload up -d --force-recreate
done
