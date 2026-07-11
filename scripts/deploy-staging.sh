#!/bin/bash
set -e

echo "Stoppping services..."
# docker stop $(docker ps -aq)
docker compose -f compose.staging.yml --profile "*" stop

echo "Starting vault agent..."
docker compose -f compose.staging.yml --profile vault-agent up -d --build

echo "Waiting for vault agent to complete current cycle..."
timeout=60
interval=5
elapsed=0
while true; do
  # Check if vault agent has successfully rendered all templates
  logs=$(docker logs crm-vault-agent-1 --tail 50 2>&1)

  if echo "$logs" | grep -q "rendered.*cert.tpl.*server.crt" &&
    echo "$logs" | grep -q "rendered.*key.tpl.*server.key"; then
    echo "Vault agent has successfully rendered all templates."
    break
  fi

  # Check for errors
  if echo "$logs" | grep -q "ERROR.*permission denied\|ERROR.*exceeded maximum retries"; then
    echo "Vault agent encountered errors."
    exit 1
  fi

  if [ "$elapsed" -ge "$timeout" ]; then
    echo "Timeout waiting for vault agent."
    exit 1
  fi

  echo "Waiting for vault agent templates... ($elapsed/$timeout seconds elapsed)"
  sleep $interval
  elapsed=$((elapsed + interval))
done

set -a
source /etc/vault/secrets/.env
set +a

echo "Starting production services..."
docker compose -f compose.staging.yml --profile prod up -d --build

echo "Enabling cert and secert watch services..."
sudo systemctl daemon-reload
sudo systemctl restart secret-reload cert-reload

echo "Deployment complete."
