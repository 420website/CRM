#!/bin/bash

# Clinical Template Persistence Startup Script
# This ensures templates are available on every deployment

echo "🚀 Starting Clinical Template Persistence Setup..."

# Ensure the persistent MongoDB directory exists
sudo mkdir -p /app/persistent-data/mongodb
sudo chown mongodb:mongodb /app/persistent-data/mongodb

# Update MongoDB configuration to use persistent storage
if [ -f /etc/mongod.conf ]; then
    sudo sed -i 's|dbPath: /var/lib/mongodb|dbPath: /app/persistent-data/mongodb|g' /etc/mongod.conf
    echo "✅ MongoDB configured for persistent storage"
fi

# Restart MongoDB with new configuration
sudo supervisorctl restart mongodb
sleep 3

# Ensure Node.js dependencies are available
cd /app && npm install mongodb

# Seed default templates
echo "🌱 Seeding clinical templates..."
cd /app && node scripts/seed-templates.js

# Restart backend to ensure everything is connected
sudo supervisorctl restart backend

echo "🎉 Clinical Template Persistence Setup Complete!"
echo "✅ Templates will now persist across all deployments"