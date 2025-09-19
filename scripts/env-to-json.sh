#!/bin/bash

ENV_FILE=".env" # Replace with your .env file name
OUT_FILE="env.json"

{
  echo "{"

  # Read each line from the .env file
  while IFS='=' read -r key value; do
    # Skip empty lines and comments
    [[ -z "$key" || "$key" =~ ^# ]] && continue

    # Escape double quotes in the value to ensure valid JSON
    escaped_value=$(echo "$value" | sed 's/"/\\"/g')

    # Format as a JSON key-value pair
    echo "  \"$key\": \"$escaped_value\","
  done <"$ENV_FILE" | sed '$s/,$//' # Remove trailing comma from last entry

  echo "}"
} >"$OUT_FILE"
