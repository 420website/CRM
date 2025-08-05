#!/usr/bin/env node

const { MongoClient } = require('mongodb');

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

async function seedNotesTemplates() {
  const mongoUrl = process.env.MONGO_URL || 'mongodb://localhost:27017';
  const dbName = process.env.DB_NAME || 'medical_db';
  
  let client;
  
  try {
    console.log('🌱 Seeding Notes templates...');
    
    client = new MongoClient(mongoUrl);
    await client.connect();
    
    const db = client.db(dbName);
    const collection = db.collection('notes_templates');
    
    // Check if Notes templates already exist
    const existingCount = await collection.countDocuments();
    
    if (existingCount === 0) {
      console.log('📥 No Notes templates found, inserting defaults...');
      
      await collection.insertMany(defaultNotesTemplates);
      console.log(`✅ Inserted ${defaultNotesTemplates.length} default Notes templates`);
    } else {
      console.log(`✅ Found ${existingCount} existing Notes templates, skipping seed`);
      
      // Ensure default Notes templates exist
      for (const template of defaultNotesTemplates) {
        const exists = await collection.findOne({ name: template.name });
        if (!exists) {
          await collection.insertOne(template);
          console.log(`✅ Added missing default Notes template: ${template.name}`);
        }
      }
    }
    
    console.log('🎉 Notes template seeding completed successfully');
    
  } catch (error) {
    console.error('❌ Error seeding Notes templates:', error);
    process.exit(1);
  } finally {
    if (client) {
      await client.close();
    }
  }
}

// Run if called directly
if (require.main === module) {
  seedNotesTemplates();
}

module.exports = { seedNotesTemplates, defaultNotesTemplates };