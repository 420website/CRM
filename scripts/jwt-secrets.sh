#!/bin/bash

echo "JWT_ACCESS_SECRET=$(openssl rand -base64 32 | tr -d '\n' | tr '+/' '-_' | tr -d '=')"
echo "MFA_ENCRYPTION_KEY=$(openssl rand -base64 32 | tr -d '\n')"
