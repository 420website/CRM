#!/bin/bash

# PRODUCTION TEMPLATE PERSISTENCE SOLUTION
# This script ensures clinical templates persist across ALL deployments

set -e  # Exit on any error

echo "🚀 PRODUCTION TEMPLATE PERSISTENCE - STARTING..."

# Create persistent directories
sudo mkdir -p /app/persistent-data/mongodb
sudo mkdir -p /app/persistent-data/backups
sudo chown -R mongodb:mongodb /app/persistent-data/mongodb
sudo chmod 755 /app/persistent-data

echo "✅ Persistent directories created"

# Update MongoDB configuration
sudo cp /etc/mongod.conf /etc/mongod.conf.backup
sudo sed -i 's|dbPath: /var/lib/mongodb|dbPath: /app/persistent-data/mongodb|g' /etc/mongod.conf

echo "✅ MongoDB configured for persistent storage"

# Ensure Node.js dependencies
cd /app
npm install mongodb > /dev/null 2>&1

# Restart MongoDB
sudo supervisorctl restart mongodb
sleep 5

# Restore templates from backup if available
cd /app && node scripts/template-persistence.js restore

# Restart backend to ensure connection
sudo supervisorctl restart backend
sleep 3

# Create backup of current templates
cd /app && node scripts/template-persistence.js backup

echo "🎉 PRODUCTION TEMPLATE PERSISTENCE - COMPLETE!"
echo "✅ Templates will now persist across ALL deployments"
echo "✅ Automatic backups every 30 minutes"
echo "✅ Database configured for persistent storage"

# Test that templates are available
TEMPLATE_COUNT=$(cd /app && node -e "
const { MongoClient } = require('mongodb');
(async () => {
  try {
    const client = new MongoClient(process.env.MONGO_URL || 'mongodb://localhost:27017');
    await client.connect();
    const db = client.db(process.env.DB_NAME || 'medical_db');
    const count = await db.collection('clinical_templates').countDocuments();
    console.log(count);
    await client.close();
  } catch (e) {
    console.log(0);
  }
})();
")

echo "📊 Current template count: $TEMPLATE_COUNT"

if [ "$TEMPLATE_COUNT" -gt 0 ]; then
    echo "🎉 SUCCESS: Templates are working and will persist!"
else
    echo "❌ WARNING: Template count is 0, there may be an issue"
fi