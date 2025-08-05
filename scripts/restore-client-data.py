#!/usr/bin/env python3
"""
Robust Client Data Restoration Script
Handles proper field mapping and data restoration
"""

import pymongo
import json
import os
import sys
from datetime import datetime
from pathlib import Path

def connect_to_mongodb():
    """Connect to MongoDB using environment variables"""
    try:
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        client = pymongo.MongoClient(mongo_url)
        db = client['my420_ca_db']
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        sys.exit(1)

def get_latest_backup():
    """Get the most recent backup file"""
    backup_dir = Path(__file__).parent.parent / 'persistent-data' / 'client-backups'
    
    if not backup_dir.exists():
        print("No backup directory found")
        return None
    
    backup_files = list(backup_dir.glob('admin-registrations-backup-*.json'))
    if not backup_files:
        print("No backup files found")
        return None
    
    # Get the most recent backup
    latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
    return latest_backup

def restore_client_data(backup_file=None, force=False):
    """Restore client data from backup with proper field mapping"""
    try:
        db = connect_to_mongodb()
        collection = db['admin_registrations']
        
        # Get backup file
        if not backup_file:
            backup_file = get_latest_backup()
        
        if not backup_file:
            print("No backup file available for restoration")
            return False
        
        print(f"Restoring from: {backup_file}")
        
        # Load backup data
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        print(f"Found {len(backup_data)} records in backup")
        
        # Check if we need to clear existing data
        current_count = collection.count_documents({})
        if current_count > 0 and not force:
            response = input(f"Database contains {current_count} records. Clear and restore? (y/N): ")
            if response.lower() != 'y':
                print("Restoration cancelled")
                return False
        
        # Clear existing data
        if current_count > 0:
            print("Clearing existing records...")
            collection.delete_many({})
        
        # Drop problematic indexes that might cause conflicts
        try:
            collection.drop_index('firstName_1_lastName_1')
            print("Dropped firstName_lastName index")
        except:
            pass
        
        # Restore each record with proper field mapping
        restored_count = 0
        errors = []
        
        for record in backup_data:
            try:
                # Map backup fields to database fields
                db_record = {
                    '_id': record['id'],
                    'first_name': record.get('firstName'),
                    'last_name': record.get('lastName'),
                    'name': f"{record.get('firstName', '')} {record.get('lastName', '')}".strip(),
                    'email': record.get('email'),
                    'phone': record.get('phone1'),
                    'dob': record.get('dob'),
                    'patient_consent': record.get('patientConsent'),
                    'gender': record.get('gender'),
                    'province': record.get('province'),
                    'disposition': record.get('disposition'),
                    'aka': record.get('aka'),
                    'age': record.get('age'),
                    'reg_date': record.get('regDate'),
                    'health_card': record.get('healthCard'),
                    'health_card_version': record.get('healthCardVersion'),
                    'referral_site': record.get('referralSite'),
                    'address': record.get('address'),
                    'unit_number': record.get('unitNumber'),
                    'city': record.get('city'),
                    'postal_code': record.get('postalCode'),
                    'phone1': record.get('phone1'),
                    'phone2': record.get('phone2'),
                    'ext1': record.get('ext1'),
                    'ext2': record.get('ext2'),
                    'leave_message': record.get('leaveMessage'),
                    'voicemail': record.get('voicemail'),
                    'text': record.get('text'),
                    'preferred_time': record.get('preferredTime'),
                    'language': record.get('language'),
                    'special_attention': record.get('specialAttention'),
                    'instructions': record.get('instructions'),
                    'photo': record.get('photo'),
                    'summary_template': record.get('summaryTemplate'),
                    'selected_template': record.get('selectedTemplate'),
                    'physician': record.get('physician'),
                    'rna_available': record.get('rnaAvailable'),
                    'rna_sample_date': record.get('rnaSampleDate'),
                    'rna_result': record.get('rnaResult'),
                    'coverage_type': record.get('coverageType'),
                    'referral_person': record.get('referralPerson'),
                    'test_type': record.get('testType'),
                    'hiv_date': record.get('hivDate'),
                    'hiv_result': record.get('hivResult'),
                    'hiv_type': record.get('hivType'),
                    'hiv_tester': record.get('hivTester'),
                    'timestamp': record.get('timestamp'),
                    'status': record.get('status'),
                    'attachments': record.get('attachments', []),
                    'created_at': record.get('created_at', record.get('timestamp')),
                    'modified_at': datetime.now().isoformat()
                }
                
                # Remove None values to avoid issues
                db_record = {k: v for k, v in db_record.items() if v is not None}
                
                # Insert the record
                collection.insert_one(db_record)
                restored_count += 1
                print(f"✓ Restored: {db_record.get('name', 'Unknown')} ({db_record.get('email', 'no email')})")
                
            except Exception as e:
                error_msg = f"Error restoring record {record.get('id', 'unknown')}: {e}"
                errors.append(error_msg)
                print(f"✗ {error_msg}")
        
        # Final verification
        final_count = collection.count_documents({})
        
        print(f"\n=== RESTORATION COMPLETE ===")
        print(f"Records restored: {restored_count}")
        print(f"Errors: {len(errors)}")
        print(f"Final database count: {final_count}")
        
        if errors:
            print("\nErrors encountered:")
            for error in errors:
                print(f"  - {error}")
        
        return restored_count > 0
        
    except Exception as e:
        print(f"Critical error during restoration: {e}")
        return False

def verify_data_integrity():
    """Verify that restored data is complete and properly formatted"""
    try:
        db = connect_to_mongodb()
        collection = db['admin_registrations']
        
        records = list(collection.find({}))
        
        print(f"\n=== DATA INTEGRITY VERIFICATION ===")
        print(f"Total records: {len(records)}")
        
        # Check for records with missing essential fields
        incomplete_records = []
        for record in records:
            if not record.get('name') or record.get('name').strip() == '':
                first_name = record.get('first_name', '').strip()
                last_name = record.get('last_name', '').strip()
                if not first_name and not last_name:
                    incomplete_records.append(record.get('_id'))
        
        if incomplete_records:
            print(f"WARNING: {len(incomplete_records)} records missing name information")
            print(f"Record IDs: {incomplete_records}")
        else:
            print("✓ All records have proper name information")
        
        # Check for duplicate records
        emails = [r.get('email') for r in records if r.get('email')]
        if len(emails) != len(set(emails)):
            print("WARNING: Duplicate email addresses found")
        else:
            print("✓ No duplicate email addresses")
        
        return len(incomplete_records) == 0
        
    except Exception as e:
        print(f"Error during verification: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Restore client data from backup')
    parser.add_argument('--backup-file', help='Specific backup file to restore from')
    parser.add_argument('--force', action='store_true', help='Force restoration without confirmation')
    parser.add_argument('--verify', action='store_true', help='Only verify data integrity')
    
    args = parser.parse_args()
    
    if args.verify:
        verify_data_integrity()
    else:
        success = restore_client_data(args.backup_file, args.force)
        if success:
            verify_data_integrity()
        sys.exit(0 if success else 1)