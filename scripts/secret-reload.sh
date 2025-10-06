#!/bin/bash

# Avoid triggering on initial start
# sleep 3m

# Remove trigger if it exists
rm -f /etc/vault/.secret-trigger

while true; do
  if [ -f /etc/vault/.cert-trigger ]; then
    rm /etc/vault/.secret-trigger
    echo "$(date) - Detected trigger, restarting secret-dependent containers"
    docker compose --profile secret-reload up -d --build
  fi
  sleep 5
done
