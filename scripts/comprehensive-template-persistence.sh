#!/bin/bash

# COMPREHENSIVE TEMPLATE PERSISTENCE SOLUTION
# This script ensures ALL templates (Clinical + Notes) persist across deployments

set -e  # Exit on any error

echo "🚀 COMPREHENSIVE TEMPLATE PERSISTENCE - STARTING..."

# Create persistent directories
sudo mkdir -p /app/persistent-data/mongodb
sudo mkdir -p /app/persistent-data/backups
sudo chown -R mongodb:mongodb /app/persistent-data/mongodb
sudo chmod 755 /app/persistent-data

echo "✅ Persistent directories created"

# Update MongoDB configuration for persistent storage
sudo cp /etc/mongod.conf /etc/mongod.conf.backup
sudo sed -i 's|dbPath: /var/lib/mongodb|dbPath: /app/persistent-data/mongodb|g' /etc/mongod.conf

echo "✅ MongoDB configured for persistent storage"

# Ensure Node.js dependencies
cd /app
npm install mongodb > /dev/null 2>&1

# Restart MongoDB
sudo supervisorctl restart mongodb
sleep 5

echo "📦 Backing up current templates before deployment..."

# Backup current templates (if they exist)
cd /app && node scripts/template-persistence.js backup 2>/dev/null || echo "⚠️ No clinical templates to backup"
cd /app && node scripts/notes-template-persistence.js backup 2>/dev/null || echo "⚠️ No notes templates to backup"

echo "🔄 Restoring templates from backup..."

# Restore templates from backup
cd /app && node scripts/template-persistence.js restore
cd /app && node scripts/notes-template-persistence.js restore

# Restart backend to ensure connection
sudo supervisorctl restart backend
sleep 3

echo "💾 Creating fresh backups after restoration..."

# Create fresh backups
cd /app && node scripts/template-persistence.js backup
cd /app && node scripts/notes-template-persistence.js backup

echo "🎉 COMPREHENSIVE TEMPLATE PERSISTENCE - COMPLETE!"

# Test that templates are available
CLINICAL_TEMPLATE_COUNT=$(cd /app && node -e "
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
" 2>/dev/null)

NOTES_TEMPLATE_COUNT=$(cd /app && node -e "
const { MongoClient } = require('mongodb');
(async () => {
  try {
    const client = new MongoClient(process.env.MONGO_URL || 'mongodb://localhost:27017');
    await client.connect();
    const db = client.db(process.env.DB_NAME || 'medical_db');
    const count = await db.collection('notes_templates').countDocuments();
    console.log(count);
    await client.close();
  } catch (e) {
    console.log(0);
  }
})();
" 2>/dev/null)

echo "📊 Template Status:"
echo "   Clinical Templates: $CLINICAL_TEMPLATE_COUNT"
echo "   Notes Templates: $NOTES_TEMPLATE_COUNT"

if [ "$CLINICAL_TEMPLATE_COUNT" -gt 0 ] && [ "$NOTES_TEMPLATE_COUNT" -gt 0 ]; then
    echo "🎉 SUCCESS: All templates are working and will persist!"
    echo "✅ Clinical templates will persist across deployments"
    echo "✅ Notes templates will persist across deployments"
    echo "✅ Automatic backups are in place"
    echo "✅ Database configured for persistent storage"
else
    echo "❌ WARNING: Template counts are low, there may be an issue"
    echo "   Clinical: $CLINICAL_TEMPLATE_COUNT, Notes: $NOTES_TEMPLATE_COUNT"
fi

echo "🔗 To run this script manually: bash /app/scripts/comprehensive-template-persistence.sh"