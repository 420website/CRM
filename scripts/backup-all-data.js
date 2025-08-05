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
