#!/bin/bash

# Avoid triggering on initial start
# sleep 3m

# Remove trigger if it exists
rm -f /etc/vault/.secret-trigger

while true; do
  if inotifywait -e create /etc/vault/.secret-trigger 2>/dev/null; then
    rm /etc/vault/.secret-trigger
    echo "$(date) - Detected trigger, restarting secret-dependent containers"
    docker compose --profile secret-reload up -d --build
  fi
done
