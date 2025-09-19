#!/bin/bash
set -e

#!/bin/bash
set -e

echo "Stoppping services..."
docker compose --profile prod stop

echo "Starting vault agent..."
docker compose --profile vault-agent up -d --build

echo "Waiting for vault agent to complete current cycle..."
timeout=60
interval=5
elapsed=0
while true; do
  # Check if vault agent has successfully rendered all templates
  logs=$(docker logs crm-vault-agent-1 --tail 50 2>&1)

  if echo "$logs" | grep -q "rendered.*secrets.tpl.*\.env" &&
    echo "$logs" | grep -q "rendered.*cert.tpl.*server.crt" &&
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
source .env
set +a

echo "Starting staging services..."
docker compose --profile staging up -d --build

echo "Waiting for certbot container to finish..."

timeout=120
interval=5
elapsed=0

while true; do
  status=$(docker inspect --format='{{.State.Status}}' "$CERTBOT_CONTAINER" 2>/dev/null || echo "not_found")

  if [ "$status" = "exited" ]; then
    exit_code=$(docker inspect --format='{{.State.ExitCode}}' "$CERTBOT_CONTAINER")
    if [ "$exit_code" -eq 0 ]; then
      echo "Certbot container finished successfully."
      break
    else
      echo "Certbot container exited with error code $exit_code."
      exit 1
    fi
  fi

  if [ "$elapsed" -ge "$timeout" ]; then
    echo "Timeout waiting for certbot container to finish."
    exit 1
  fi

  echo "Certbot container status: $status. Waiting... ($elapsed/$timeout seconds elapsed)"
  sleep $interval
  elapsed=$((elapsed + interval))
done

echo "Checking if certificate file exists..."

if docker run --rm -v "$CERTBOT_VOLUME:/data" busybox sh -c "[ -f /data/live/$DOMAIN_ROOT/fullchain.pem ]"; then
  echo "Certificate found!"
else
  echo "Certificate not found!"
  exit 1
fi

echo "Stopping staging services..."
docker compose --profile staging stop

echo "Starting production services..."
docker compose --profile prod up -d --build

echo "Deployment complete."
