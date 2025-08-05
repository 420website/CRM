const { MongoClient } = require('mongodb');
const fs = require('fs');
const path = require('path');

const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017';
const DB_NAME = process.env.DB_NAME || 'my420_ca_db';

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
