#!/usr/bin/env node

const { MongoClient } = require('mongodb');
const fs = require('fs');
const path = require('path');

const BACKUP_FILE = '/app/persistent-data/notes-templates-backup.json';

// Default Notes templates that should always be available
const defaultNotesTemplates = [
  {
    id: 'consultation-default',
    name: 'Consultation',
    content: '',
    is_default: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 'lab-default',
    name: 'Lab',
    content: '',
    is_default: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 'prescription-default',
    name: 'Prescription',
    content: '',
    is_default: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

async function backupNotesTemplates() {
  const mongoUrl = process.env.MONGO_URL || 'mongodb://localhost:27017';
  const dbName = process.env.DB_NAME || 'medical_db';
  
  let client;
  
  try {
    client = new MongoClient(mongoUrl);
    await client.connect();
    
    const db = client.db(dbName);
    const collection = db.collection('notes_templates');
    
    const templates = await collection.find({}).toArray();
    
    // Ensure backup directory exists
    const backupDir = path.dirname(BACKUP_FILE);
    if (!fs.existsSync(backupDir)) {
      fs.mkdirSync(backupDir, { recursive: true });
    }
    
    fs.writeFileSync(BACKUP_FILE, JSON.stringify(templates, null, 2));
    console.log(`✅ Backed up ${templates.length} Notes templates to ${BACKUP_FILE}`);
    
  } catch (error) {
    console.error('❌ Error backing up Notes templates:', error);
  } finally {
    if (client) {
      await client.close();
    }
  }
}

async function restoreNotesTemplates() {
  const mongoUrl = process.env.MONGO_URL || 'mongodb://localhost:27017';
  const dbName = process.env.DB_NAME || 'medical_db';
  
  let client;
  
  try {
    let templatesToRestore = defaultNotesTemplates;
    
    // Try to load from backup first
    if (fs.existsSync(BACKUP_FILE)) {
      try {
        const backupData = fs.readFileSync(BACKUP_FILE, 'utf8');
        const backupTemplates = JSON.parse(backupData);
        if (backupTemplates.length > 0) {
          templatesToRestore = backupTemplates;
          console.log(`📥 Loaded ${backupTemplates.length} Notes templates from backup`);
        }
      } catch (error) {
        console.log('⚠️ Notes templates backup file corrupted, using defaults');
      }
    } else {
      console.log('⚠️ No Notes templates backup found, using defaults');
    }
    
    client = new MongoClient(mongoUrl);
    await client.connect();
    
    const db = client.db(dbName);
    const collection = db.collection('notes_templates');
    
    // Clear existing templates and restore from backup
    await collection.deleteMany({});
    
    if (templatesToRestore.length > 0) {
      await collection.insertMany(templatesToRestore);
      console.log(`✅ Restored ${templatesToRestore.length} Notes templates to database`);
    }
    
  } catch (error) {
    console.error('❌ Error restoring Notes templates:', error);
  } finally {
    if (client) {
      await client.close();
    }
  }
}

// Command line interface
const command = process.argv[2];

if (command === 'backup') {
  backupNotesTemplates();
} else if (command === 'restore') {
  restoreNotesTemplates();
} else {
  console.log('Usage: node notes-template-persistence.js [backup|restore]');
  process.exit(1);
}