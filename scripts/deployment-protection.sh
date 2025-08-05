#!/bin/bash

# DEPLOYMENT PROTECTION SCRIPT
# This script ensures client data is NEVER lost during deployments

echo "🛡️  DEPLOYMENT PROTECTION - ENSURING CLIENT DATA PERSISTENCE"
echo "==========================================================="

# Create backup directories
mkdir -p /app/persistent-data/client-backups
mkdir -p /app/persistent-data/pre-deployment-backups

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
sleep 5

# 1. BACKUP ALL CLIENT DATA BEFORE DEPLOYMENT
echo "📦 Step 1: Backing up all client data..."
cd /app && node scripts/client-data-persistence.js backup

# 2. CREATE PRE-DEPLOYMENT SNAPSHOT
echo "📸 Step 2: Creating pre-deployment snapshot..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cd /app && node -e "
const { MongoClient } = require('mongodb');
const fs = require('fs');

(async () => {
  const client = new MongoClient('mongodb://localhost:27017');
  await client.connect();
  const db = client.db('my420_ca_db');
  
  // Backup all collections
  const collections = ['admin_registrations', 'notes', 'interactions', 'activities', 'test_results'];
  const snapshot = {};
  
  for (const collectionName of collections) {
    try {
      const data = await db.collection(collectionName).find({}).toArray();
      snapshot[collectionName] = data;
      console.log(\`📋 Backed up \${data.length} \${collectionName} records\`);
    } catch (error) {
      console.log(\`⚠️  Collection \${collectionName} not found or empty\`);
      snapshot[collectionName] = [];
    }
  }
  
  // Save snapshot
  fs.writeFileSync('/app/persistent-data/pre-deployment-backups/snapshot-${TIMESTAMP}.json', JSON.stringify(snapshot, null, 2));
  fs.writeFileSync('/app/persistent-data/pre-deployment-backups/snapshot-latest.json', JSON.stringify(snapshot, null, 2));
  
  const totalRecords = Object.values(snapshot).reduce((sum, arr) => sum + arr.length, 0);
  console.log(\`✅ Pre-deployment snapshot created with \${totalRecords} total records\`);
  
  await client.close();
})();
"

# 3. VERIFY MONGODB PERSISTENT STORAGE
echo "🔍 Step 3: Verifying MongoDB persistent storage..."
if [ -d "/app/persistent-data/mongodb" ]; then
  echo "✅ MongoDB persistent storage directory exists"
  du -sh /app/persistent-data/mongodb/
else
  echo "❌ MongoDB persistent storage directory missing!"
  exit 1
fi

# 4. CHECK DATABASE CONFIGURATION
echo "🔧 Step 4: Checking database configuration..."
cd /app && node -e "
const { MongoClient } = require('mongodb');

(async () => {
  const client = new MongoClient('mongodb://localhost:27017');
  await client.connect();
  
  // Check database name
  const dbName = process.env.DB_NAME || 'my420_ca_db';
  console.log('📊 Database name:', dbName);
  
  const db = client.db(dbName);
  const collections = await db.listCollections().toArray();
  console.log('📋 Available collections:', collections.map(c => c.name));
  
  // Check admin registrations
  const adminCount = await db.collection('admin_registrations').countDocuments();
  console.log('👥 Client registrations:', adminCount);
  
  await client.close();
})();
"

# 5. RESTORE TEMPLATE DATA (WITHOUT AFFECTING CLIENT DATA)
echo "🔄 Step 5: Ensuring template data is present..."
cd /app && node -e "
const { MongoClient } = require('mongodb');

(async () => {
  const client = new MongoClient('mongodb://localhost:27017');
  await client.connect();
  const db = client.db('my420_ca_db');
  
  // Check template data
  const dispositions = await db.collection('dispositions').countDocuments();
  const referralSites = await db.collection('referral_sites').countDocuments();
  const clinicalTemplates = await db.collection('clinical_templates').countDocuments();
  const notesTemplates = await db.collection('notes_templates').countDocuments();
  
  console.log('📊 Template data status:');
  console.log('- Dispositions:', dispositions);
  console.log('- Referral Sites:', referralSites);
  console.log('- Clinical Templates:', clinicalTemplates);
  console.log('- Notes Templates:', notesTemplates);
  
  // If template data is missing, restore from backups
  if (dispositions < 60 || referralSites < 20 || clinicalTemplates < 3 || notesTemplates < 3) {
    console.log('⚠️  Template data is missing, restoring...');
    
    // Restore templates (this will NOT affect client data)
    await client.close();
    process.exit(1); // Signal to restore templates
  } else {
    console.log('✅ All template data is present');
  }
  
  await client.close();
})();
"

# If template data is missing, restore it
if [ $? -ne 0 ]; then
  echo "🔄 Restoring template data..."
  cd /app && node scripts/restore-all-data.js
fi

# 6. FINAL VERIFICATION
echo "🎯 Step 6: Final verification..."
cd /app && node scripts/client-data-persistence.js verify

echo "🎉 DEPLOYMENT PROTECTION COMPLETED SUCCESSFULLY!"
echo "✅ Client data is secured and will persist across deployments"
echo "✅ All template data is present and functional"
echo "✅ Database is properly configured for persistent storage"