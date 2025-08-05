#!/usr/bin/env node

const { MongoClient } = require('mongodb');
const fs = require('fs');
const path = require('path');

const BACKUP_FILE = '/app/persistent-data/clinical-templates-backup.json';

// Default templates that should always be available
const defaultTemplates = [
  {
    id: 'positive-default',
    name: 'Positive',
    content: 'Dx 10+ years ago and treated. RNA - no labs available. However, has had ongoing risk factors with sharing pipes and straws. Counselled regarding risk factors. Point of care test was completed for HCV and tested positive at approximately two minutes with a dark line. HIV testing came back negative. Collected a DBS specimen and advised that it will take approximately 7 to 10 days for results. Referral: none. Client does have a valid address and has also provided a phone number for results.',
    is_default: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 'negative-pipes-default',
    name: 'Negative - Pipes',
    content: '',
    is_default: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 'negative-pipes-straws-default',
    name: 'Negative - Pipes/Straws',
    content: '',
    is_default: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 'negative-pipes-straws-needles-default',
    name: 'Negative - Pipes/Straws/Needles',
    content: '',
    is_default: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

async function backupTemplates() {
  const mongoUrl = process.env.MONGO_URL || 'mongodb://localhost:27017';
  const dbName = process.env.DB_NAME || 'medical_db';
  
  let client;
  
  try {
    client = new MongoClient(mongoUrl);
    await client.connect();
    
    const db = client.db(dbName);
    const collection = db.collection('clinical_templates');
    
    const templates = await collection.find({}).toArray();
    
    // Ensure backup directory exists
    const backupDir = path.dirname(BACKUP_FILE);
    if (!fs.existsSync(backupDir)) {
      fs.mkdirSync(backupDir, { recursive: true });
    }
    
    fs.writeFileSync(BACKUP_FILE, JSON.stringify(templates, null, 2));
    console.log(`✅ Backed up ${templates.length} templates to ${BACKUP_FILE}`);
    
  } catch (error) {
    console.error('❌ Error backing up templates:', error);
  } finally {
    if (client) {
      await client.close();
    }
  }
}

async function restoreTemplates() {
  const mongoUrl = process.env.MONGO_URL || 'mongodb://localhost:27017';
  const dbName = process.env.DB_NAME || 'medical_db';
  
  let client;
  
  try {
    let templatesToRestore = defaultTemplates;
    
    // Try to load from backup first
    if (fs.existsSync(BACKUP_FILE)) {
      try {
        const backupData = fs.readFileSync(BACKUP_FILE, 'utf8');
        const backupTemplates = JSON.parse(backupData);
        if (backupTemplates.length > 0) {
          templatesToRestore = backupTemplates;
          console.log(`📥 Loaded ${backupTemplates.length} templates from backup`);
        }
      } catch (error) {
        console.log('⚠️ Backup file corrupted, using defaults');
      }
    }
    
    client = new MongoClient(mongoUrl);
    await client.connect();
    
    const db = client.db(dbName);
    const collection = db.collection('clinical_templates');
    
    // Clear existing templates and restore from backup
    await collection.deleteMany({});
    
    if (templatesToRestore.length > 0) {
      await collection.insertMany(templatesToRestore);
      console.log(`✅ Restored ${templatesToRestore.length} templates to database`);
    }
    
  } catch (error) {
    console.error('❌ Error restoring templates:', error);
  } finally {
    if (client) {
      await client.close();
    }
  }
}

// Command line interface
const command = process.argv[2];

if (command === 'backup') {
  backupTemplates();
} else if (command === 'restore') {
  restoreTemplates();
} else {
  console.log('Usage: node template-persistence.js [backup|restore]');
  process.exit(1);
}