#!/bin/bash

# COMPREHENSIVE PRODUCTION DATA PERSISTENCE SOLUTION
# This script ensures ALL data (templates, dispositions, referral sites) persist across deployments

set -e  # Exit on any error

echo "🚀 COMPREHENSIVE PRODUCTION DATA PERSISTENCE - STARTING..."

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

# Restore all data from backups if available
echo "📥 Restoring all data from backups..."
cd /app && node scripts/template-persistence.js restore
cd /app && node scripts/notes-template-persistence.js restore

# Restart backend to ensure connection and trigger seeding
echo "🔄 Restarting backend to trigger seeding..."
sudo supervisorctl restart backend
sleep 5

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 10

# Create comprehensive backup of current data
echo "💾 Creating comprehensive backup..."
cd /app && node scripts/template-persistence.js backup
cd /app && node scripts/notes-template-persistence.js backup

# Create a comprehensive backup script for all data types
cat > /app/scripts/backup-all-data.js << 'EOF'
const { MongoClient } = require('mongodb');
const fs = require('fs');
const path = require('path');

const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017';
const DB_NAME = process.env.DB_NAME || 'medical_db';

async function backupAllData() {
  const client = new MongoClient(MONGO_URL);
  
  try {
    await client.connect();
    const db = client.db(DB_NAME);
    
    // Create backup directory
    const backupDir = '/app/persistent-data/backups';
    if (!fs.existsSync(backupDir)) {
      fs.mkdirSync(backupDir, { recursive: true });
    }
    
    // Backup clinical templates
    const clinicalTemplates = await db.collection('clinical_templates').find({}).toArray();
    fs.writeFileSync(path.join(backupDir, 'clinical-templates-backup.json'), JSON.stringify(clinicalTemplates, null, 2));
    console.log(`✅ Backed up ${clinicalTemplates.length} clinical templates`);
    
    // Backup notes templates
    const notesTemplates = await db.collection('notes_templates').find({}).toArray();
    fs.writeFileSync(path.join(backupDir, 'notes-templates-backup.json'), JSON.stringify(notesTemplates, null, 2));
    console.log(`✅ Backed up ${notesTemplates.length} notes templates`);
    
    // Backup dispositions
    const dispositions = await db.collection('dispositions').find({}).toArray();
    fs.writeFileSync(path.join(backupDir, 'dispositions-backup.json'), JSON.stringify(dispositions, null, 2));
    console.log(`✅ Backed up ${dispositions.length} dispositions`);
    
    // Backup referral sites
    const referralSites = await db.collection('referral_sites').find({}).toArray();
    fs.writeFileSync(path.join(backupDir, 'referral-sites-backup.json'), JSON.stringify(referralSites, null, 2));
    console.log(`✅ Backed up ${referralSites.length} referral sites`);
    
    console.log('🎉 Comprehensive backup completed successfully!');
    
  } catch (error) {
    console.error('❌ Error during backup:', error);
    process.exit(1);
  } finally {
    await client.close();
  }
}

backupAllData();
EOF

# Create a comprehensive restore script for all data types
cat > /app/scripts/restore-all-data.js << 'EOF'
const { MongoClient } = require('mongodb');
const fs = require('fs');
const path = require('path');

const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017';
const DB_NAME = process.env.DB_NAME || 'medical_db';

async function restoreAllData() {
  const client = new MongoClient(MONGO_URL);
  
  try {
    await client.connect();
    const db = client.db(DB_NAME);
    
    const backupDir = '/app/persistent-data/backups';
    
    // Restore clinical templates
    const clinicalBackupPath = path.join(backupDir, 'clinical-templates-backup.json');
    if (fs.existsSync(clinicalBackupPath)) {
      const clinicalTemplates = JSON.parse(fs.readFileSync(clinicalBackupPath, 'utf8'));
      if (clinicalTemplates.length > 0) {
        await db.collection('clinical_templates').deleteMany({});
        await db.collection('clinical_templates').insertMany(clinicalTemplates);
        console.log(`✅ Restored ${clinicalTemplates.length} clinical templates`);
      }
    }
    
    // Restore notes templates
    const notesBackupPath = path.join(backupDir, 'notes-templates-backup.json');
    if (fs.existsSync(notesBackupPath)) {
      const notesTemplates = JSON.parse(fs.readFileSync(notesBackupPath, 'utf8'));
      if (notesTemplates.length > 0) {
        await db.collection('notes_templates').deleteMany({});
        await db.collection('notes_templates').insertMany(notesTemplates);
        console.log(`✅ Restored ${notesTemplates.length} notes templates`);
      }
    }
    
    // Restore dispositions
    const dispositionsBackupPath = path.join(backupDir, 'dispositions-backup.json');
    if (fs.existsSync(dispositionsBackupPath)) {
      const dispositions = JSON.parse(fs.readFileSync(dispositionsBackupPath, 'utf8'));
      if (dispositions.length > 0) {
        await db.collection('dispositions').deleteMany({});
        await db.collection('dispositions').insertMany(dispositions);
        console.log(`✅ Restored ${dispositions.length} dispositions`);
      }
    }
    
    // Restore referral sites
    const referralSitesBackupPath = path.join(backupDir, 'referral-sites-backup.json');
    if (fs.existsSync(referralSitesBackupPath)) {
      const referralSites = JSON.parse(fs.readFileSync(referralSitesBackupPath, 'utf8'));
      if (referralSites.length > 0) {
        await db.collection('referral_sites').deleteMany({});
        await db.collection('referral_sites').insertMany(referralSites);
        console.log(`✅ Restored ${referralSites.length} referral sites`);
      }
    }
    
    console.log('🎉 Comprehensive restore completed successfully!');
    
  } catch (error) {
    console.error('❌ Error during restore:', error);
    process.exit(1);
  } finally {
    await client.close();
  }
}

restoreAllData();
EOF

# Run the comprehensive backup
echo "💾 Running comprehensive backup..."
cd /app && node scripts/backup-all-data.js

# Test that all data is available
echo "🧪 Testing data availability..."
TOTAL_COUNT=$(cd /app && node -e "
const { MongoClient } = require('mongodb');
(async () => {
  try {
    const client = new MongoClient(process.env.MONGO_URL || 'mongodb://localhost:27017');
    await client.connect();
    const db = client.db(process.env.DB_NAME || 'medical_db');
    
    const clinical = await db.collection('clinical_templates').countDocuments();
    const notes = await db.collection('notes_templates').countDocuments();
    const dispositions = await db.collection('dispositions').countDocuments();
    const referralSites = await db.collection('referral_sites').countDocuments();
    
    console.log('Clinical Templates:', clinical);
    console.log('Notes Templates:', notes);
    console.log('Dispositions:', dispositions);
    console.log('Referral Sites:', referralSites);
    console.log('Total:', clinical + notes + dispositions + referralSites);
    
    await client.close();
  } catch (e) {
    console.log('Error:', e.message);
  }
})();
")

echo "📊 Current data counts:"
echo "$TOTAL_COUNT"

echo ""
echo "🎉 COMPREHENSIVE PRODUCTION DATA PERSISTENCE - COMPLETE!"
echo "✅ All data (templates, dispositions, referral sites) will persist across deployments"
echo "✅ Automatic backups created in /app/persistent-data/backups/"
echo "✅ Database configured for persistent storage"
echo "✅ Restoration scripts available for future deployments"