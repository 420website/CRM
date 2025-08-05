#!/bin/sh
set -e

# Read command and directory from Supervisor config
CONFIG_FILE=/app/etc/supervisor/conf.d/supervisord.conf
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Supervisor config $CONFIG_FILE not found, exiting"
    exit 1
fi

# Extract backend section and get command and directory
BACKEND_SECTION=$(sed -n '/^\[program:backend\]/,/^\[/p' "$CONFIG_FILE" | grep -v '^\[program:backend\]' | grep -v '^\[')
COMMAND=$(echo "$BACKEND_SECTION" | grep -E '^\s*command=' | cut -d'=' -f2-)
DIRECTORY=$(echo "$BACKEND_SECTION" | grep -E '^\s*directory=' | cut -d'=' -f2-)

# Remove --reload flag if present
COMMAND=$(echo "$COMMAND" | sed 's/--reload//g')

# Normalize COMMAND: strip any directory prefix from the executable
first_token=${COMMAND%% *}
rest=${COMMAND#"$first_token"}
COMMAND="${first_token##*/}${rest}"

if [ -z "$COMMAND" ]; then
    echo "Backend command not found in supervisor config, exiting"
    exit 1
fi

if [ -z "$DIRECTORY" ]; then
    echo "Backend directory not found in supervisor config, using default /app/backend"
    DIRECTORY="/app/backend"
fi

echo "Starting FastAPI backend: $COMMAND in $DIRECTORY"
cd "$DIRECTORY" || cd /app/backend
eval "$COMMAND" &
BACKEND_PID=$!

echo "Waiting for backend to start..."
sleep 30

if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "Backend failed to start at initialization, exiting"
    exit 1
fi

# Start Nginx
nginx -g 'daemon off;' &
NGINX_PID=$!

# Handle termination signals
trap 'kill $BACKEND_PID $NGINX_PID; exit 0' SIGTERM SIGINT

# Check if processes are still running
while kill -0 $BACKEND_PID 2>/dev/null && kill -0 $NGINX_PID 2>/dev/null; do
    sleep 1
done

# If we get here, one of the processes died
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "Nginx died, shutting down backend..."
    kill $BACKEND_PID
else
    echo "Backend died, shutting down nginx..."
    kill $NGINX_PID
fi

exit 1