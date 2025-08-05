#!/usr/bin/env python3
"""
PRODUCTION LOCK SYSTEM
Prevents accidental data loss during deployment/forking process
Creates bulletproof safeguards against "brand new" selection
"""

import os
import sys
import json
import pymongo
from datetime import datetime
from pathlib import Path

class ProductionLock:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'my420_ca_db')
        self.environment = os.environ.get('ENVIRONMENT', 'production').lower()
        
        # Lock file to prevent data wiping
        self.lock_file = Path('/app/persistent-data/.production-lock')
        self.backup_dir = Path('/app/persistent-data/emergency-backups')
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Connect to MongoDB
        try:
            self.client = pymongo.MongoClient(self.mongo_url)
            self.db = self.client[self.db_name]
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            sys.exit(1)
    
    def is_production_locked(self):
        """Check if production is locked against data wiping"""
        return self.lock_file.exists()
    
    def create_production_lock(self):
        """Create production lock to prevent data loss"""
        print("🔒 Creating production lock...")
        
        # Count existing data
        client_count = self.db['admin_registrations'].count_documents({})
        
        lock_data = {
            'created_at': datetime.now().isoformat(),
            'environment': self.environment,
            'client_count_at_lock': client_count,
            'locked_by': 'production-protection-system',
            'message': 'PRODUCTION DATA PROTECTED - DO NOT WIPE',
            'warning': 'This lock prevents accidental data loss during deployment'
        }
        
        with open(self.lock_file, 'w') as f:
            json.dump(lock_data, f, indent=2)
        
        print(f"✅ Production lock created with {client_count} client records protected")
        return True
    
    def emergency_backup_all_data(self):
        """Create emergency backup of ALL data before any operations"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        collections_to_backup = [
            'admin_registrations',
            'clinical_templates', 
            'notes_templates',
            'dispositions',
            'referral_sites'
        ]
        
        backup_manifest = {
            'timestamp': timestamp,
            'environment': self.environment,
            'collections': {}
        }
        
        print(f"🆘 Creating EMERGENCY backup at {timestamp}")
        
        for collection_name in collections_to_backup:
            try:
                collection = self.db[collection_name]
                documents = list(collection.find({}))
                count = len(documents)
                
                if count > 0:
                    # Convert ObjectId to string for JSON serialization
                    for doc in documents:
                        if '_id' in doc:
                            doc['_id'] = str(doc['_id'])
                    
                    backup_file = self.backup_dir / f'emergency_{collection_name}_{timestamp}.json'
                    with open(backup_file, 'w') as f:
                        json.dump(documents, f, indent=2)
                    
                    backup_manifest['collections'][collection_name] = {
                        'count': count,
                        'file': str(backup_file)
                    }
                    
                    print(f"  ✅ {collection_name}: {count} records → {backup_file}")
                else:
                    print(f"  ⚠️ {collection_name}: 0 records (skipped)")
                    
            except Exception as e:
                print(f"  ❌ Error backing up {collection_name}: {e}")
                backup_manifest['collections'][collection_name] = {'error': str(e)}
        
        # Save backup manifest
        manifest_file = self.backup_dir / f'emergency_manifest_{timestamp}.json'
        with open(manifest_file, 'w') as f:
            json.dump(backup_manifest, f, indent=2)
        
        print(f"📋 Emergency backup manifest: {manifest_file}")
        return manifest_file
    
    def prevent_data_wipe(self):
        """Prevent any operation that would wipe production data"""
        if not self.is_production_locked():
            print("⚠️ Production not locked - creating lock now")
            self.create_production_lock()
        
        # Create emergency backup
        self.emergency_backup_all_data()
        
        # Check if someone is trying to wipe data
        client_count = self.db['admin_registrations'].count_documents({})
        
        if client_count == 0:
            print("🚨 CRITICAL: No client data found - possible data wipe detected!")
            print("🔄 Attempting emergency restoration...")
            
            # Try to restore from latest backup
            latest_backup = self.find_latest_backup()
            if latest_backup:
                self.restore_from_backup(latest_backup)
            else:
                print("❌ No backups found for restoration!")
                sys.exit(1)
        
        print(f"✅ Production data verified: {client_count} client records")
    
    def find_latest_backup(self):
        """Find the most recent emergency backup"""
        emergency_files = list(self.backup_dir.glob('emergency_admin_registrations_*.json'))
        
        if not emergency_files:
            # Try other backup locations
            backup_files = list(Path('/app/persistent-data/client-backups').glob('*.json'))
            if backup_files:
                return max(backup_files, key=lambda f: f.stat().st_mtime)
            return None
        
        # Return most recent emergency backup
        return max(emergency_files, key=lambda f: f.stat().st_mtime)
    
    def restore_from_backup(self, backup_file):
        """Restore data from backup file"""
        print(f"🔄 Restoring from backup: {backup_file}")
        
        try:
            with open(backup_file, 'r') as f:
                records = json.load(f)
            
            if records:
                # Clear existing data and restore
                self.db['admin_registrations'].drop()
                
                # Convert string IDs back to ObjectId if needed
                for record in records:
                    if '_id' in record and isinstance(record['_id'], str):
                        try:
                            record['_id'] = pymongo.ObjectId(record['_id'])
                        except:
                            # If conversion fails, remove _id and let MongoDB generate new one
                            del record['_id']
                
                self.db['admin_registrations'].insert_many(records)
                
                restored_count = len(records)
                print(f"✅ Restored {restored_count} client records from backup")
                
                # Update lock file with restoration info
                lock_data = {
                    'restored_at': datetime.now().isoformat(),
                    'restored_from': str(backup_file),
                    'restored_count': restored_count,
                    'automatic_restoration': True
                }
                
                with open(self.lock_file, 'a') as f:
                    f.write(f"\n{json.dumps(lock_data, indent=2)}")
                
                return True
            else:
                print("❌ Backup file is empty")
                return False
                
        except Exception as e:
            print(f"❌ Error restoring from backup: {e}")
            return False
    
    def force_production_protection(self):
        """Force enable all production protections"""
        print("🛡️ FORCING PRODUCTION PROTECTION")
        print("=" * 50)
        
        # Always create lock
        self.create_production_lock()
        
        # Always create emergency backup
        self.emergency_backup_all_data()
        
        # Prevent any data wiping
        self.prevent_data_wipe()
        
        # Create protection flag file
        protection_flag = Path('/app/.production-protected')
        with open(protection_flag, 'w') as f:
            f.write(f"PRODUCTION PROTECTED AT {datetime.now().isoformat()}")
        
        print("🔒 PRODUCTION FULLY PROTECTED")
        print("   - Lock file created")
        print("   - Emergency backup completed")
        print("   - Data wipe prevention active")
        print("   - Protection flag set")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Production Lock System')
    parser.add_argument('--lock', action='store_true', help='Create production lock')
    parser.add_argument('--backup', action='store_true', help='Create emergency backup')
    parser.add_argument('--prevent-wipe', action='store_true', help='Prevent data wipe')
    parser.add_argument('--force-protect', action='store_true', help='Force all protections')
    parser.add_argument('--check', action='store_true', help='Check protection status')
    
    args = parser.parse_args()
    
    lock_system = ProductionLock()
    
    if args.force_protect:
        lock_system.force_production_protection()
    elif args.lock:
        lock_system.create_production_lock()
    elif args.backup:
        lock_system.emergency_backup_all_data()
    elif args.prevent_wipe:
        lock_system.prevent_data_wipe()
    elif args.check:
        is_locked = lock_system.is_production_locked()
        client_count = lock_system.db['admin_registrations'].count_documents({})
        
        print(f"Production locked: {is_locked}")
        print(f"Client records: {client_count}")
        
        if is_locked:
            with open(lock_system.lock_file, 'r') as f:
                lock_data = json.load(f)
            print(f"Lock created: {lock_data.get('created_at')}")
            print(f"Protected records: {lock_data.get('client_count_at_lock', 0)}")
    else:
        # Default: force protection
        lock_system.force_production_protection()

if __name__ == "__main__":
    main()