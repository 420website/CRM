#!/usr/bin/env python3
"""
Environment Separation Protection Script
Ensures test data doesn't contaminate production environment
"""

import os
import sys
import pymongo
import json
from datetime import datetime
from pathlib import Path

class EnvironmentProtection:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'my420_ca_db')
        self.is_production = os.environ.get('ENVIRONMENT', 'production').lower() == 'production'
        
        # Connect to MongoDB
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.db_name]
        
        # Test data patterns to identify
        self.test_patterns = [
            'test', 'TestConnectivity', 'TestUser', 'ConnectivityTest',
            'dummy', 'sample', 'demo', 'fake', 'mock'
        ]
    
    def identify_test_records(self):
        """Identify records that appear to be test data"""
        collection = self.db['admin_registrations']
        
        test_records = []
        all_records = list(collection.find({}))
        
        for record in all_records:
            # Check various fields for test patterns
            is_test = False
            
            # Check name fields
            first_name = (record.get('first_name') or '').lower()
            last_name = (record.get('last_name') or '').lower()
            name = (record.get('name') or '').lower()
            email = (record.get('email') or '').lower()
            
            # Check if any field contains test patterns
            for pattern in self.test_patterns:
                if (pattern in first_name or pattern in last_name or 
                    pattern in name or pattern in email):
                    is_test = True
                    break
            
            # Check for obviously fake emails
            if email and ('test@' in email or 'example.com' in email):
                is_test = True
            
            if is_test:
                test_records.append({
                    '_id': record.get('_id'),
                    'name': record.get('name', 'Unknown'),
                    'email': record.get('email', 'No email'),
                    'first_name': record.get('first_name'),
                    'last_name': record.get('last_name')
                })
        
        return test_records
    
    def clean_test_data(self, auto_confirm=False):
        """Remove test data from production environment"""
        if not self.is_production:
            print("Not in production environment, skipping test data cleanup")
            return
        
        test_records = self.identify_test_records()
        
        if not test_records:
            print("✓ No test data found in production")
            return
        
        print(f"Found {len(test_records)} test records:")
        for record in test_records:
            print(f"  - {record['name']} ({record['email']})")
        
        if not auto_confirm:
            response = input("\nRemove these test records from production? (y/N): ")
            if response.lower() != 'y':
                print("Test data cleanup cancelled")
                return
        
        # Remove test records
        collection = self.db['admin_registrations']
        removed_count = 0
        
        for record in test_records:
            try:
                result = collection.delete_one({'_id': record['_id']})
                if result.deleted_count > 0:
                    removed_count += 1
                    print(f"✓ Removed: {record['name']}")
            except Exception as e:
                print(f"✗ Error removing {record['name']}: {e}")
        
        print(f"\nRemoved {removed_count} test records from production")
    
    def create_production_backup(self):
        """Create a clean production backup without test data"""
        collection = self.db['admin_registrations']
        all_records = list(collection.find({}))
        
        # Filter out test records
        test_records = self.identify_test_records()
        test_ids = {r['_id'] for r in test_records}
        
        production_records = [r for r in all_records if r.get('_id') not in test_ids]
        
        # Convert to standardized format
        standardized_records = []
        for record in production_records:
            standardized = {
                'id': record.get('_id'),
                'firstName': record.get('first_name'),
                'lastName': record.get('last_name'),
                'email': record.get('email'),
                'phone1': record.get('phone1') or record.get('phone'),
                'dob': record.get('dob'),
                'patientConsent': record.get('patient_consent'),
                'gender': record.get('gender'),
                'province': record.get('province'),
                'disposition': record.get('disposition'),
                'aka': record.get('aka'),
                'age': record.get('age'),
                'regDate': record.get('reg_date'),
                'healthCard': record.get('health_card'),
                'healthCardVersion': record.get('health_card_version'),
                'referralSite': record.get('referral_site'),
                'address': record.get('address'),
                'unitNumber': record.get('unit_number'),
                'city': record.get('city'),
                'postalCode': record.get('postal_code'),
                'phone2': record.get('phone2'),
                'ext1': record.get('ext1'),
                'ext2': record.get('ext2'),
                'leaveMessage': record.get('leave_message'),
                'voicemail': record.get('voicemail'),
                'text': record.get('text'),
                'preferredTime': record.get('preferred_time'),
                'language': record.get('language'),
                'specialAttention': record.get('special_attention'),
                'instructions': record.get('instructions'),
                'photo': record.get('photo'),
                'summaryTemplate': record.get('summary_template'),
                'selectedTemplate': record.get('selected_template'),
                'physician': record.get('physician'),
                'rnaAvailable': record.get('rna_available'),
                'rnaSampleDate': record.get('rna_sample_date'),
                'rnaResult': record.get('rna_result'),
                'coverageType': record.get('coverage_type'),
                'referralPerson': record.get('referral_person'),
                'testType': record.get('test_type'),
                'hivDate': record.get('hiv_date'),
                'hivResult': record.get('hiv_result'),
                'hivType': record.get('hiv_type'),
                'hivTester': record.get('hiv_tester'),
                'timestamp': record.get('timestamp'),
                'status': record.get('status'),
                'attachments': record.get('attachments', []),
                'created_at': record.get('created_at'),
                'modified_at': record.get('modified_at')
            }
            standardized_records.append(standardized)
        
        # Save production backup
        backup_dir = Path('/app/persistent-data/client-backups')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f'production-clean-backup-{timestamp}.json'
        
        with open(backup_file, 'w') as f:
            json.dump(standardized_records, f, indent=2)
        
        print(f"✓ Clean production backup created: {backup_file}")
        print(f"  - Total records: {len(all_records)}")
        print(f"  - Test records excluded: {len(test_records)}")
        print(f"  - Production records: {len(production_records)}")
        
        return backup_file
    
    def verify_environment_separation(self):
        """Verify that production environment is properly separated from test"""
        print("=== ENVIRONMENT SEPARATION VERIFICATION ===")
        
        # Check environment variables
        print(f"Environment: {os.environ.get('ENVIRONMENT', 'not set')}")
        print(f"Database: {self.db_name}")
        print(f"MongoDB URL: {self.mongo_url}")
        
        # Check for test data
        test_records = self.identify_test_records()
        if test_records:
            print(f"⚠️  WARNING: Found {len(test_records)} test records in production")
            for record in test_records:
                print(f"   - {record['name']} ({record['email']})")
        else:
            print("✓ No test data found in production")
        
        # Check record quality
        collection = self.db['admin_registrations']
        total_records = collection.count_documents({})
        
        # Check for records with missing essential data
        incomplete_records = collection.count_documents({
            '$or': [
                {'first_name': {'$in': [None, '']}},
                {'last_name': {'$in': [None, '']}},
                {'name': {'$in': [None, '']}}
            ]
        })
        
        print(f"Total records: {total_records}")
        print(f"Incomplete records: {incomplete_records}")
        
        if incomplete_records > 0:
            print("⚠️  WARNING: Found records with missing essential data")
        else:
            print("✓ All records have essential data")
        
        return len(test_records) == 0 and incomplete_records == 0

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Environment separation protection')
    parser.add_argument('--clean', action='store_true', help='Clean test data from production')
    parser.add_argument('--backup', action='store_true', help='Create clean production backup')
    parser.add_argument('--verify', action='store_true', help='Verify environment separation')
    parser.add_argument('--auto-confirm', action='store_true', help='Auto-confirm actions')
    
    args = parser.parse_args()
    
    protection = EnvironmentProtection()
    
    if args.clean:
        protection.clean_test_data(args.auto_confirm)
    
    if args.backup:
        protection.create_production_backup()
    
    if args.verify or not any([args.clean, args.backup]):
        is_clean = protection.verify_environment_separation()
        sys.exit(0 if is_clean else 1)

if __name__ == "__main__":
    main()