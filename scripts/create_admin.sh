#!/bin/bash

# admin.sh - Wrapper script for Python admin tool

set -e

# Check if Python script exists
if [ ! -f "/scripts/wait-for-db.sh" ]; then
  echo "❌ /scripts/wait-for-db.sh  not found"
  exit 1
fi

/scripts/wait-for-db.sh

# Check if Python script exists
if [ ! -f "/backend/scripts/create_admin.py" ]; then
  echo "❌ create_admin.py not found"
  echo "Make sure the Python script is in the current directory"
  exit 1
fi

# Run the Python script
echo "Starting admin user creation..."
cd /backend
PYTHONPATH=/backend python scripts/create_admin.py

echo "Admin User seeding finished. Starting backend..."
exec "$@"
