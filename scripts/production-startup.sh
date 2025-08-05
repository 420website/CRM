#!/bin/bash

# PRODUCTION STARTUP SCRIPT
# This script ensures all data is loaded on production deployments

echo "🚀 PRODUCTION STARTUP - ENSURING ALL DATA IS LOADED"
echo "=" * 60

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
sleep 5

# Check current data counts
echo "📊 Checking current data counts..."
cd /app && node -e "
const { MongoClient } = require('mongodb');
(async () => {
  try {
    const client = new MongoClient('mongodb://localhost:27017');
    await client.connect();
    const db = client.db('my420_ca_db');
    
    const clinical = await db.collection('clinical_templates').countDocuments();
    const notes = await db.collection('notes_templates').countDocuments();
    const dispositions = await db.collection('dispositions').countDocuments();
    const referralSites = await db.collection('referral_sites').countDocuments();
    
    console.log('Current counts:');
    console.log('- Clinical Templates:', clinical);
    console.log('- Notes Templates:', notes);
    console.log('- Dispositions:', dispositions);
    console.log('- Referral Sites:', referralSites);
    
    // Check if data is missing
    const totalExpected = 94; // 4 + 3 + 62 + 25
    const totalActual = clinical + notes + dispositions + referralSites;
    
    if (totalActual < totalExpected) {
      console.log('❌ Data is missing! Expected:', totalExpected, 'Actual:', totalActual);
      process.exit(1);
    } else {
      console.log('✅ All data is present!');
    }
    
    await client.close();
  } catch (e) {
    console.log('❌ Database connection failed:', e.message);
    process.exit(1);
  }
})();
"

# If data is missing, restore from backups
if [ $? -ne 0 ]; then
  echo "📥 Restoring data from backups..."
  cd /app && node scripts/restore-all-data.js
  
  # If restore fails, force seed
  if [ $? -ne 0 ]; then
    echo "🔄 Force seeding data..."
    cd /app && node scripts/force-seed-data.js
  fi
fi

# Final verification
echo "🔍 Final verification..."
cd /app && node -e "
const { MongoClient } = require('mongodb');
(async () => {
  const client = new MongoClient('mongodb://localhost:27017');
  await client.connect();
  const db = client.db('my420_ca_db');
  
  const clinical = await db.collection('clinical_templates').countDocuments();
  const notes = await db.collection('notes_templates').countDocuments();
  const dispositions = await db.collection('dispositions').countDocuments();
  const referralSites = await db.collection('referral_sites').countDocuments();
  
  console.log('📊 FINAL VERIFICATION:');
  console.log('- Clinical Templates:', clinical);
  console.log('- Notes Templates:', notes);
  console.log('- Dispositions:', dispositions);
  console.log('- Referral Sites:', referralSites);
  console.log('- TOTAL:', clinical + notes + dispositions + referralSites);
  
  await client.close();
})();
"

echo "🎉 PRODUCTION STARTUP COMPLETE - ALL DATA LOADED!"