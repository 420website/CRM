#!/bin/bash

while inotifywait -e create /etc/vault/.secret-trigger 2>/dev/null; do
  rm /etc/vault/.secret-trigger
  docker compose --profile secret-reload up -d --force-recreate
done
