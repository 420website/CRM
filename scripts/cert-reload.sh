#!/bin/bash

# Remove trigger if it exists
rm -f /etc/vault/.cert-trigger

while true; do
  if [ -f /etc/vault/.cert-trigger ]; then
    rm -f /etc/vault/.cert-trigger
    echo "$(date) - Detected trigger, restarting cert-dependent containers"
    docker compose -p crm --profile cert-reload restart
  fi
  sleep 5
done
