#!/usr/bin/env python3
"""
Comprehensive Backup Script for All Production Data
Ensures all templates and data are backed up properly
"""

import pymongo
import json
import os
import sys
from datetime import datetime
from pathlib import Path

def create_comprehensive_backup():
    """Create a complete backup of all production data"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        client = pymongo.MongoClient(mongo_url)
        db = client['my420_ca_db']
        
        # Create backup directory
        backup_dir = Path('/app/persistent-data/backups')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        print("🔄 Starting comprehensive backup...")
        
        # Backup clinical templates
        print("📋 Backing up clinical templates...")
        clinical_templates = list(db.clinical_templates.find({}))
        if clinical_templates:
            backup_path = backup_dir / 'clinical-templates-backup.json'
            # Convert ObjectId to string for JSON serialization
            for template in clinical_templates:
                if '_id' in template:
                    del template['_id']
            
            with open(backup_path, 'w') as f:
                json.dump(clinical_templates, f, indent=2, default=str)
            print(f"✅ Backed up {len(clinical_templates)} clinical templates")
        else:
            print("⚠️  No clinical templates found")
        
        # Backup notes templates
        print("📝 Backing up notes templates...")
        notes_templates = list(db.notes_templates.find({}))
        if notes_templates:
            backup_path = backup_dir / 'notes-templates-backup.json'
            # Convert ObjectId to string for JSON serialization
            for template in notes_templates:
                if '_id' in template:
                    del template['_id']
            
            with open(backup_path, 'w') as f:
                json.dump(notes_templates, f, indent=2, default=str)
            print(f"✅ Backed up {len(notes_templates)} notes templates")
        else:
            print("⚠️  No notes templates found")
            
        # Backup dispositions
        print("📊 Backing up dispositions...")
        dispositions = list(db.dispositions.find({}))
        if dispositions:
            backup_path = backup_dir / 'dispositions-backup.json'
            # Convert ObjectId to string for JSON serialization
            for disposition in dispositions:
                if '_id' in disposition:
                    del disposition['_id']
            
            with open(backup_path, 'w') as f:
                json.dump(dispositions, f, indent=2, default=str)
            print(f"✅ Backed up {len(dispositions)} dispositions")
        else:
            print("⚠️  No dispositions found")
            
        # Backup referral sites
        print("🏥 Backing up referral sites...")
        referral_sites = list(db.referral_sites.find({}))
        if referral_sites:
            backup_path = backup_dir / 'referral-sites-backup.json'
            # Convert ObjectId to string for JSON serialization
            for site in referral_sites:
                if '_id' in site:
                    del site['_id']
            
            with open(backup_path, 'w') as f:
                json.dump(referral_sites, f, indent=2, default=str)
            print(f"✅ Backed up {len(referral_sites)} referral sites")
        else:
            print("⚠️  No referral sites found")
        
        # Backup client registrations
        print("👤 Backing up client registrations...")
        client_registrations = list(db.admin_registrations.find({}))
        if client_registrations:
            client_backup_dir = Path('/app/persistent-data/client-backups')
            client_backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create timestamped backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = client_backup_dir / f'admin-registrations-backup-{timestamp}.json'
            
            # Convert to standardized format for client registrations
            standardized_registrations = []
            for registration in client_registrations:
                standardized = {
                    'id': registration.get('_id'),
                    'firstName': registration.get('first_name'),
                    'lastName': registration.get('last_name'),
                    'email': registration.get('email'),
                    'phone1': registration.get('phone1') or registration.get('phone'),
                    'dob': registration.get('dob'),
                    'patientConsent': registration.get('patient_consent'),
                    'gender': registration.get('gender'),
                    'province': registration.get('province'),
                    'disposition': registration.get('disposition'),
                    'aka': registration.get('aka'),
                    'age': registration.get('age'),
                    'regDate': registration.get('reg_date'),
                    'healthCard': registration.get('health_card'),
                    'healthCardVersion': registration.get('health_card_version'),
                    'referralSite': registration.get('referral_site'),
                    'address': registration.get('address'),
                    'unitNumber': registration.get('unit_number'),
                    'city': registration.get('city'),
                    'postalCode': registration.get('postal_code'),
                    'phone2': registration.get('phone2'),
                    'ext1': registration.get('ext1'),
                    'ext2': registration.get('ext2'),
                    'leaveMessage': registration.get('leave_message'),
                    'voicemail': registration.get('voicemail'),
                    'text': registration.get('text'),
                    'preferredTime': registration.get('preferred_time'),
                    'language': registration.get('language'),
                    'specialAttention': registration.get('special_attention'),
                    'instructions': registration.get('instructions'),
                    'photo': registration.get('photo'),
                    'summaryTemplate': registration.get('summary_template'),
                    'selectedTemplate': registration.get('selected_template'),
                    'physician': registration.get('physician'),
                    'rnaAvailable': registration.get('rna_available'),
                    'rnaSampleDate': registration.get('rna_sample_date'),
                    'rnaResult': registration.get('rna_result'),
                    'coverageType': registration.get('coverage_type'),
                    'referralPerson': registration.get('referral_person'),
                    'testType': registration.get('test_type'),
                    'hivDate': registration.get('hiv_date'),
                    'hivResult': registration.get('hiv_result'),
                    'hivType': registration.get('hiv_type'),
                    'hivTester': registration.get('hiv_tester'),
                    'timestamp': registration.get('timestamp'),
                    'status': registration.get('status'),
                    'attachments': registration.get('attachments', []),
                    'created_at': registration.get('created_at'),
                    'modified_at': registration.get('modified_at')
                }
                standardized_registrations.append(standardized)
            
            with open(backup_path, 'w') as f:
                json.dump(standardized_registrations, f, indent=2, default=str)
            print(f"✅ Backed up {len(client_registrations)} client registrations")
            
            # Create latest backup
            latest_backup = client_backup_dir / 'admin-registrations-latest.json'
            with open(latest_backup, 'w') as f:
                json.dump(standardized_registrations, f, indent=2, default=str)
        else:
            print("⚠️  No client registrations found")
        
        print("✅ Comprehensive backup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during backup: {e}")
        return False

def verify_backup_integrity():
    """Verify that backup files exist and contain data"""
    backup_dir = Path('/app/persistent-data/backups')
    client_backup_dir = Path('/app/persistent-data/client-backups')
    
    print("🔍 Verifying backup integrity...")
    
    files_to_check = [
        (backup_dir / 'clinical-templates-backup.json', 'Clinical Templates'),
        (backup_dir / 'notes-templates-backup.json', 'Notes Templates'),
        (backup_dir / 'dispositions-backup.json', 'Dispositions'),
        (backup_dir / 'referral-sites-backup.json', 'Referral Sites'),
        (client_backup_dir / 'admin-registrations-latest.json', 'Client Registrations')
    ]
    
    all_good = True
    
    for file_path, name in files_to_check:
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    count = len(data) if isinstance(data, list) else 1
                    print(f"✅ {name}: {count} records")
            except Exception as e:
                print(f"❌ {name}: Error reading file - {e}")
                all_good = False
        else:
            print(f"❌ {name}: File not found")
            all_good = False
    
    return all_good

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive backup script')
    parser.add_argument('--backup', action='store_true', help='Create comprehensive backup')
    parser.add_argument('--verify', action='store_true', help='Verify backup integrity')
    
    args = parser.parse_args()
    
    if args.backup or not any([args.verify]):
        success = create_comprehensive_backup()
        if success and args.verify:
            verify_backup_integrity()
        sys.exit(0 if success else 1)
    
    if args.verify:
        integrity_good = verify_backup_integrity()
        sys.exit(0 if integrity_good else 1)