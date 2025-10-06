#!/bin/bash

# Remove trigger if it exists
rm -f /etc/vault/.secret-trigger

while true; do
  inotifywait -e create /etc/vault/.secret-trigger 2>/dev/null
  rm /etc/vault/.secret-trigger
  echo "$(date) - Detected trigger, restarting secret-dependent containers"
  docker compose --profile secret-reload up -d --force-recreate
done
