#!/bin/bash

while inotifywait -e create /etc/vault/.cert-trigger 2>/dev/null; do
  rm /etc/vault/.cert-trigger
  docker compose --profile cert-reload up -d --force-recreate
done
