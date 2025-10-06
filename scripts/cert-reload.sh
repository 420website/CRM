#!/bin/bash

# Avoid triggering on initial start
# sleep 3m

# Remove trigger if it exists
rm -f /etc/vault/.cert-trigger

while true; do
  if [ -f /etc/vault/.cert-trigger ]; then
    rm -f /etc/vault/.cert-trigger
    echo "$(date) - Detected trigger, restarting cert-dependent containers"
    docker compose --profile cert-reload up -d --build
  fi
  sleep 5 # avoid tight loop
done
