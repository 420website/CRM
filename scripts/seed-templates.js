#!/usr/bin/env node

const { MongoClient } = require('mongodb');

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

async function seedTemplates() {
  const mongoUrl = process.env.MONGO_URL || 'mongodb://localhost:27017';
  const dbName = process.env.DB_NAME || 'medical_db';
  
  let client;
  
  try {
    console.log('🌱 Seeding clinical templates...');
    
    client = new MongoClient(mongoUrl);
    await client.connect();
    
    const db = client.db(dbName);
    const collection = db.collection('clinical_templates');
    
    // Check if templates already exist
    const existingCount = await collection.countDocuments();
    
    if (existingCount === 0) {
      console.log('📥 No templates found, inserting defaults...');
      
      await collection.insertMany(defaultTemplates);
      console.log(`✅ Inserted ${defaultTemplates.length} default templates`);
    } else {
      console.log(`✅ Found ${existingCount} existing templates, skipping seed`);
      
      // Ensure default templates exist
      for (const template of defaultTemplates) {
        const exists = await collection.findOne({ name: template.name });
        if (!exists) {
          await collection.insertOne(template);
          console.log(`✅ Added missing default template: ${template.name}`);
        }
      }
    }
    
    console.log('🎉 Template seeding completed successfully');
    
  } catch (error) {
    console.error('❌ Error seeding templates:', error);
    process.exit(1);
  } finally {
    if (client) {
      await client.close();
    }
  }
}

// Run if called directly
if (require.main === module) {
  seedTemplates();
}

module.exports = { seedTemplates, defaultTemplates };