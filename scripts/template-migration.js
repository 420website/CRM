#!/usr/bin/env node

const { MongoClient } = require('mongodb');
const fs = require('fs');
const path = require('path');

// Export templates from current environment to migration file
async function exportTemplatesForMigration() {
  const mongoUrl = process.env.MONGO_URL || 'mongodb://localhost:27017';
  const dbName = process.env.DB_NAME || 'medical_db';
  
  let client;
  
  try {
    client = new MongoClient(mongoUrl);
    await client.connect();
    
    const db = client.db(dbName);
    
    // Get all clinical templates
    const clinicalTemplates = await db.collection('clinical_templates').find({}).toArray();
    
    // Get all notes templates
    const notesTemplates = await db.collection('notes_templates').find({}).toArray();
    
    const migrationData = {
      export_date: new Date().toISOString(),
      environment: process.env.NODE_ENV || 'development',
      clinical_templates: clinicalTemplates,
      notes_templates: notesTemplates,
      total_templates: clinicalTemplates.length + notesTemplates.length
    };
    
    // Create migration file
    const migrationFile = `/app/template-migration-${Date.now()}.json`;
    fs.writeFileSync(migrationFile, JSON.stringify(migrationData, null, 2));
    
    console.log(`✅ MIGRATION EXPORT COMPLETED`);
    console.log(`📁 Migration file created: ${migrationFile}`);
    console.log(`📊 Exported ${clinicalTemplates.length} clinical templates`);
    console.log(`📊 Exported ${notesTemplates.length} notes templates`);
    console.log(`📊 Total templates: ${migrationData.total_templates}`);
    
    return migrationFile;
    
  } catch (error) {
    console.error('❌ Error exporting templates:', error);
    throw error;
  } finally {
    if (client) {
      await client.close();
    }
  }
}

// Import templates from migration file to current environment
async function importTemplatesFromMigration(migrationFile) {
  const mongoUrl = process.env.MONGO_URL || 'mongodb://localhost:27017';
  const dbName = process.env.DB_NAME || 'medical_db';
  
  let client;
  
  try {
    if (!fs.existsSync(migrationFile)) {
      throw new Error(`Migration file not found: ${migrationFile}`);
    }
    
    const migrationData = JSON.parse(fs.readFileSync(migrationFile, 'utf8'));
    
    client = new MongoClient(mongoUrl);
    await client.connect();
    
    const db = client.db(dbName);
    
    // Import clinical templates
    if (migrationData.clinical_templates && migrationData.clinical_templates.length > 0) {
      await db.collection('clinical_templates').deleteMany({});
      await db.collection('clinical_templates').insertMany(migrationData.clinical_templates);
      console.log(`✅ Imported ${migrationData.clinical_templates.length} clinical templates`);
    }
    
    // Import notes templates
    if (migrationData.notes_templates && migrationData.notes_templates.length > 0) {
      await db.collection('notes_templates').deleteMany({});
      await db.collection('notes_templates').insertMany(migrationData.notes_templates);
      console.log(`✅ Imported ${migrationData.notes_templates.length} notes templates`);
    }
    
    console.log(`🎉 MIGRATION IMPORT COMPLETED`);
    console.log(`📅 Original export date: ${migrationData.export_date}`);
    console.log(`🌍 Original environment: ${migrationData.environment}`);
    console.log(`📊 Total templates imported: ${migrationData.total_templates}`);
    
    // Create fresh backups after import
    const backupResult = await Promise.all([
      require('/app/scripts/template-persistence.js'),
      require('/app/scripts/notes-template-persistence.js')
    ]);
    
    console.log(`💾 Fresh backups created after import`);
    
  } catch (error) {
    console.error('❌ Error importing templates:', error);
    throw error;
  } finally {
    if (client) {
      await client.close();
    }
  }
}

// Command line interface
const command = process.argv[2];
const migrationFile = process.argv[3];

if (command === 'export') {
  exportTemplatesForMigration();
} else if (command === 'import' && migrationFile) {
  importTemplatesFromMigration(migrationFile);
} else {
  console.log('Template Migration System');
  console.log('');
  console.log('Usage:');
  console.log('  Export templates: node template-migration.js export');
  console.log('  Import templates: node template-migration.js import <migration-file>');
  console.log('');
  console.log('Workflow:');
  console.log('  1. In testing environment: node template-migration.js export');
  console.log('  2. Copy migration file to production');
  console.log('  3. In production: node template-migration.js import <migration-file>');
  process.exit(1);
}