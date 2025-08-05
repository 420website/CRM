const { MongoClient } = require('mongodb');
const fs = require('fs');
const path = require('path');

// Use environment variables or defaults
const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017';
const DB_NAME = process.env.DB_NAME || 'my420_ca_db';

// Backup directory for client data
const CLIENT_BACKUP_DIR = '/app/persistent-data/client-backups';

// Ensure backup directory exists
if (!fs.existsSync(CLIENT_BACKUP_DIR)) {
  fs.mkdirSync(CLIENT_BACKUP_DIR, { recursive: true });
}

async function backupClientData() {
  console.log('🔄 Backing up client registration data...');
  
  const client = new MongoClient(MONGO_URL);
  
  try {
    await client.connect();
    const db = client.db(DB_NAME);
    
    // Backup admin registrations (client data) with proper field mapping
    const adminRegistrations = await db.collection('admin_registrations').find({}).toArray();
    
    if (adminRegistrations.length > 0) {
      // Convert to standardized format with proper field mapping
      const standardizedRegistrations = adminRegistrations.map(reg => ({
        id: reg._id,
        firstName: reg.first_name,
        lastName: reg.last_name,
        email: reg.email,
        phone1: reg.phone1 || reg.phone,
        dob: reg.dob,
        patientConsent: reg.patient_consent,
        gender: reg.gender,
        province: reg.province,
        disposition: reg.disposition,
        aka: reg.aka,
        age: reg.age,
        regDate: reg.reg_date,
        healthCard: reg.health_card,
        healthCardVersion: reg.health_card_version,
        referralSite: reg.referral_site,
        address: reg.address,
        unitNumber: reg.unit_number,
        city: reg.city,
        postalCode: reg.postal_code,
        phone2: reg.phone2,
        ext1: reg.ext1,
        ext2: reg.ext2,
        leaveMessage: reg.leave_message,
        voicemail: reg.voicemail,
        text: reg.text,
        preferredTime: reg.preferred_time,
        language: reg.language,
        specialAttention: reg.special_attention,
        instructions: reg.instructions,
        photo: reg.photo,
        summaryTemplate: reg.summary_template,
        selectedTemplate: reg.selected_template,
        physician: reg.physician,
        rnaAvailable: reg.rna_available,
        rnaSampleDate: reg.rna_sample_date,
        rnaResult: reg.rna_result,
        coverageType: reg.coverage_type,
        referralPerson: reg.referral_person,
        testType: reg.test_type,
        hivDate: reg.hiv_date,
        hivResult: reg.hiv_result,
        hivType: reg.hiv_type,
        hivTester: reg.hiv_tester,
        timestamp: reg.timestamp,
        status: reg.status,
        attachments: reg.attachments || [],
        created_at: reg.created_at,
        modified_at: reg.modified_at
      }));
      
      const timestamp = new Date().toISOString().replace(/:/g, '-').split('.')[0];
      const backupPath = path.join(CLIENT_BACKUP_DIR, `admin-registrations-backup-${timestamp}.json`);
      
      fs.writeFileSync(backupPath, JSON.stringify(standardizedRegistrations, null, 2));
      console.log(`✅ Backed up ${standardizedRegistrations.length} client registrations to ${backupPath}`);
      
      // Also create a "latest" backup for easy restore
      const latestBackupPath = path.join(CLIENT_BACKUP_DIR, 'admin-registrations-latest.json');
      fs.writeFileSync(latestBackupPath, JSON.stringify(standardizedRegistrations, null, 2));
      console.log(`✅ Latest backup created at ${latestBackupPath}`);
    } else {
      console.log('ℹ️ No client registrations found to backup');
    }
    
    // Backup other client-related collections
    const collections = ['notes', 'interactions', 'activities', 'test_results'];
    
    for (const collectionName of collections) {
      try {
        const data = await db.collection(collectionName).find({}).toArray();
        if (data.length > 0) {
          const timestamp = new Date().toISOString().replace(/:/g, '-').split('.')[0];
          const backupPath = path.join(CLIENT_BACKUP_DIR, `${collectionName}-backup-${timestamp}.json`);
          fs.writeFileSync(backupPath, JSON.stringify(data, null, 2));
          console.log(`✅ Backed up ${data.length} ${collectionName} records`);
        }
      } catch (error) {
        console.log(`ℹ️ Collection ${collectionName} not found or empty`);
      }
    }
    
    console.log('🎉 Client data backup completed successfully!');
    
  } catch (error) {
    console.error('❌ Error during client data backup:', error);
    throw error;
  } finally {
    await client.close();
  }
}

async function restoreClientData() {
  console.log('🔄 Restoring client registration data...');
  
  const client = new MongoClient(MONGO_URL);
  
  try {
    await client.connect();
    const db = client.db(DB_NAME);
    
    // Restore admin registrations from latest backup
    const latestBackupPath = path.join(CLIENT_BACKUP_DIR, 'admin-registrations-latest.json');
    
    if (fs.existsSync(latestBackupPath)) {
      const adminRegistrations = JSON.parse(fs.readFileSync(latestBackupPath, 'utf8'));
      
      if (adminRegistrations.length > 0) {
        // Check if data already exists
        const existingCount = await db.collection('admin_registrations').countDocuments();
        
        if (existingCount === 0) {
          // Only restore if no data exists
          await db.collection('admin_registrations').insertMany(adminRegistrations);
          console.log(`✅ Restored ${adminRegistrations.length} client registrations`);
        } else {
          console.log(`ℹ️ Client registrations already exist (${existingCount} records), skipping restore`);
        }
      }
    } else {
      console.log('ℹ️ No client registration backup found');
    }
    
    // Restore other client-related collections
    const collections = ['notes', 'interactions', 'activities', 'test_results'];
    
    for (const collectionName of collections) {
      try {
        const backupFiles = fs.readdirSync(CLIENT_BACKUP_DIR)
          .filter(file => file.startsWith(`${collectionName}-backup-`) && file.endsWith('.json'))
          .sort()
          .reverse(); // Most recent first
        
        if (backupFiles.length > 0) {
          const latestBackupFile = backupFiles[0];
          const backupPath = path.join(CLIENT_BACKUP_DIR, latestBackupFile);
          const data = JSON.parse(fs.readFileSync(backupPath, 'utf8'));
          
          if (data.length > 0) {
            const existingCount = await db.collection(collectionName).countDocuments();
            
            if (existingCount === 0) {
              await db.collection(collectionName).insertMany(data);
              console.log(`✅ Restored ${data.length} ${collectionName} records`);
            } else {
              console.log(`ℹ️ ${collectionName} already exists (${existingCount} records), skipping restore`);
            }
          }
        }
      } catch (error) {
        console.log(`ℹ️ No backup found for ${collectionName} or error restoring: ${error.message}`);
      }
    }
    
    console.log('🎉 Client data restore completed successfully!');
    
  } catch (error) {
    console.error('❌ Error during client data restore:', error);
    throw error;
  } finally {
    await client.close();
  }
}

async function verifyClientDataPersistence() {
  console.log('🔍 Verifying client data persistence...');
  
  const client = new MongoClient(MONGO_URL);
  
  try {
    await client.connect();
    const db = client.db(DB_NAME);
    
    // Check admin registrations
    const adminRegistrationsCount = await db.collection('admin_registrations').countDocuments();
    console.log(`📊 Admin registrations in database: ${adminRegistrationsCount}`);
    
    // Check backup files
    const backupFiles = fs.readdirSync(CLIENT_BACKUP_DIR)
      .filter(file => file.startsWith('admin-registrations-backup-') && file.endsWith('.json'));
    
    console.log(`📁 Client data backup files: ${backupFiles.length}`);
    
    if (backupFiles.length > 0) {
      const latestBackupFile = backupFiles.sort().reverse()[0];
      const backupPath = path.join(CLIENT_BACKUP_DIR, latestBackupFile);
      const backupData = JSON.parse(fs.readFileSync(backupPath, 'utf8'));
      console.log(`📋 Latest backup contains: ${backupData.length} registrations`);
      console.log(`📅 Latest backup file: ${latestBackupFile}`);
    }
    
    // Show recent registrations
    const recentRegistrations = await db.collection('admin_registrations')
      .find({})
      .sort({ timestamp: -1 })
      .limit(5)
      .toArray();
    
    console.log('🔍 Recent client registrations:');
    recentRegistrations.forEach((reg, index) => {
      console.log(`  ${index + 1}. ${reg.firstName} ${reg.lastName} - ${reg.status} - ${reg.timestamp}`);
    });
    
    console.log('✅ Client data persistence verification completed!');
    
  } catch (error) {
    console.error('❌ Error during client data verification:', error);
    throw error;
  } finally {
    await client.close();
  }
}

// Export functions for use in other scripts
module.exports = {
  backupClientData,
  restoreClientData,
  verifyClientDataPersistence
};

// If run directly, execute the backup
if (require.main === module) {
  const command = process.argv[2];
  
  switch (command) {
    case 'backup':
      backupClientData().catch(console.error);
      break;
    case 'restore':
      restoreClientData().catch(console.error);
      break;
    case 'verify':
      verifyClientDataPersistence().catch(console.error);
      break;
    default:
      console.log('Usage: node client-data-persistence.js [backup|restore|verify]');
      process.exit(1);
  }
}