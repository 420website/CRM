#!/usr/bin/env python3
"""
CRITICAL SEEDING INVESTIGATION TEST
==================================

This test investigates the critical issue where templates, dispositions, and referral sites 
are not being saved or imported into production. Users lose all their data on deployment.

Test Focus:
1. Current Database State - Check counts of all seeded data
2. Seeding Functions Status - Verify if seeding functions are working
3. Critical Issue Investigation - Check initialize_database() function
4. Backup/Restore System - Verify backup files and restore functionality
"""

import requests
import json
import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

class SeedingInvestigationTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json'}
        self.tests_run = 0
        self.tests_passed = 0
        
        # Load MongoDB connection details
        load_dotenv('/app/backend/.env')
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'my420_ca_db')
        
        print("🚨 CRITICAL SEEDING INVESTIGATION STARTED")
        print("=" * 60)
        print(f"🔗 Backend URL: {self.base_url}")
        print(f"🗄️  MongoDB URL: {self.mongo_url}")
        print(f"📊 Database Name: {self.db_name}")
        print("=" * 60)

    def run_test(self, name, test_func):
        """Run a single test with error handling"""
        self.tests_run += 1
        print(f"\n🔍 {name}")
        print("-" * 50)
        
        try:
            success = test_func()
            if success:
                self.tests_passed += 1
                print(f"✅ {name} - PASSED")
            else:
                print(f"❌ {name} - FAILED")
            return success
        except Exception as e:
            print(f"❌ {name} - ERROR: {str(e)}")
            return False

    def check_database_state(self):
        """1. Check current database state - counts of all seeded data"""
        print("📊 CHECKING CURRENT DATABASE STATE")
        
        try:
            client = MongoClient(self.mongo_url)
            db = client[self.db_name]
            
            # Check clinical templates
            clinical_count = db.clinical_templates.count_documents({})
            clinical_default_count = db.clinical_templates.count_documents({"is_default": True})
            print(f"📋 Clinical Templates: {clinical_count} total ({clinical_default_count} default)")
            
            # Check notes templates  
            notes_count = db.notes_templates.count_documents({})
            notes_default_count = db.notes_templates.count_documents({"is_default": True})
            print(f"📝 Notes Templates: {notes_count} total ({notes_default_count} default)")
            
            # Check dispositions
            dispositions_count = db.dispositions.count_documents({})
            dispositions_default_count = db.dispositions.count_documents({"is_default": True})
            print(f"🏥 Dispositions: {dispositions_count} total ({dispositions_default_count} default)")
            
            # Check referral sites
            referral_sites_count = db.referral_sites.count_documents({})
            referral_sites_default_count = db.referral_sites.count_documents({"is_default": True})
            print(f"🏢 Referral Sites: {referral_sites_count} total ({referral_sites_default_count} default)")
            
            # Check if any data exists
            total_seeded_data = clinical_count + notes_count + dispositions_count + referral_sites_count
            
            if total_seeded_data == 0:
                print("🚨 CRITICAL ISSUE: NO SEEDED DATA FOUND IN DATABASE!")
                print("   This confirms the user's report that data is not persisting.")
                return False
            elif clinical_count == 0 or notes_count == 0 or dispositions_count == 0 or referral_sites_count == 0:
                print("⚠️  WARNING: Some seeded data collections are empty!")
                print("   This indicates partial seeding failure.")
                return False
            else:
                print("✅ All seeded data collections contain data.")
                return True
                
        except Exception as e:
            print(f"❌ Error checking database state: {str(e)}")
            return False

    def check_api_endpoints(self):
        """Check if API endpoints for seeded data are working"""
        print("🌐 CHECKING API ENDPOINTS FOR SEEDED DATA")
        
        endpoints = [
            ("Clinical Templates", "/api/clinical-templates"),
            ("Notes Templates", "/api/notes-templates"), 
            ("Dispositions", "/api/dispositions"),
            ("Referral Sites", "/api/referral-sites")
        ]
        
        all_working = True
        
        for name, endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else 0
                    print(f"✅ {name}: {count} items via API")
                else:
                    print(f"❌ {name}: API returned status {response.status_code}")
                    all_working = False
            except Exception as e:
                print(f"❌ {name}: API error - {str(e)}")
                all_working = False
                
        return all_working

    def check_seeding_scripts(self):
        """2. Check if seeding scripts exist and are executable"""
        print("📜 CHECKING SEEDING SCRIPTS")
        
        scripts = [
            "/app/scripts/seed-templates.js",
            "/app/scripts/seed-notes-templates.js",
            "/app/scripts/template-persistence.js",
            "/app/scripts/notes-template-persistence.js",
            "/app/scripts/comprehensive-template-persistence.sh"
        ]
        
        all_exist = True
        
        for script in scripts:
            if os.path.exists(script):
                print(f"✅ {script} - EXISTS")
                # Check if it's executable
                if os.access(script, os.X_OK):
                    print(f"   ✅ Executable permissions OK")
                else:
                    print(f"   ⚠️  Not executable (may be OK for .js files)")
            else:
                print(f"❌ {script} - MISSING")
                all_exist = False
                
        return all_exist

    def test_seeding_functions_manually(self):
        """3. Test seeding functions manually to see if they work"""
        print("🔧 TESTING SEEDING FUNCTIONS MANUALLY")
        
        # Test clinical templates seeding
        print("\n📋 Testing Clinical Templates Seeding...")
        try:
            result = subprocess.run([
                'node', '/app/scripts/seed-templates.js'
            ], capture_output=True, text=True, cwd="/app", env={
                **os.environ,
                'MONGO_URL': self.mongo_url,
                'DB_NAME': self.db_name
            })
            
            if result.returncode == 0:
                print("✅ Clinical templates seeding script executed successfully")
                print(f"   Output: {result.stdout}")
            else:
                print("❌ Clinical templates seeding script failed")
                print(f"   Error: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error running clinical templates seeding: {str(e)}")
            return False
            
        # Test notes templates seeding
        print("\n📝 Testing Notes Templates Seeding...")
        try:
            result = subprocess.run([
                'node', '/app/scripts/seed-notes-templates.js'
            ], capture_output=True, text=True, cwd="/app", env={
                **os.environ,
                'MONGO_URL': self.mongo_url,
                'DB_NAME': self.db_name
            })
            
            if result.returncode == 0:
                print("✅ Notes templates seeding script executed successfully")
                print(f"   Output: {result.stdout}")
            else:
                print("❌ Notes templates seeding script failed")
                print(f"   Error: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error running notes templates seeding: {str(e)}")
            return False
            
        return True

    def check_backup_system(self):
        """4. Check backup/restore system"""
        print("💾 CHECKING BACKUP/RESTORE SYSTEM")
        
        backup_dirs = [
            "/app/persistent-data",
            "/app/backups"
        ]
        
        backup_files = [
            "/app/persistent-data/clinical-templates-backup.json",
            "/app/persistent-data/notes-templates-backup.json"
        ]
        
        # Check backup directories
        for backup_dir in backup_dirs:
            if os.path.exists(backup_dir):
                print(f"✅ Backup directory exists: {backup_dir}")
                # List contents
                try:
                    contents = os.listdir(backup_dir)
                    print(f"   Contents: {contents}")
                except Exception as e:
                    print(f"   ❌ Error listing contents: {str(e)}")
            else:
                print(f"❌ Backup directory missing: {backup_dir}")
                
        # Check backup files
        backup_files_exist = True
        for backup_file in backup_files:
            if os.path.exists(backup_file):
                print(f"✅ Backup file exists: {backup_file}")
                # Check file size
                try:
                    size = os.path.getsize(backup_file)
                    print(f"   Size: {size} bytes")
                    if size == 0:
                        print(f"   ⚠️  WARNING: Backup file is empty!")
                        backup_files_exist = False
                except Exception as e:
                    print(f"   ❌ Error checking file size: {str(e)}")
            else:
                print(f"❌ Backup file missing: {backup_file}")
                backup_files_exist = False
                
        return backup_files_exist

    def check_server_startup_logs(self):
        """Check server startup logs for seeding information"""
        print("📋 CHECKING SERVER STARTUP LOGS")
        
        try:
            # Check supervisor logs for backend
            result = subprocess.run([
                'tail', '-n', '100', '/var/log/supervisor/backend.out.log'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logs = result.stdout
                print("📋 Recent backend startup logs:")
                print("-" * 30)
                
                # Look for seeding-related messages
                seeding_messages = []
                for line in logs.split('\n'):
                    if any(keyword in line.lower() for keyword in [
                        'seed', 'template', 'disposition', 'referral', 'initialize', 'backup'
                    ]):
                        seeding_messages.append(line)
                        
                if seeding_messages:
                    print("🔍 Seeding-related log messages:")
                    for msg in seeding_messages[-10:]:  # Last 10 messages
                        print(f"   {msg}")
                else:
                    print("⚠️  No seeding-related messages found in recent logs")
                    
                print("-" * 30)
                return True
            else:
                print("❌ Could not read backend logs")
                return False
                
        except Exception as e:
            print(f"❌ Error checking server logs: {str(e)}")
            return False

    def test_initialize_database_function(self):
        """Test if initialize_database function is being called"""
        print("🚀 TESTING INITIALIZE_DATABASE FUNCTION")
        
        # Check if the function exists in the backend code
        backend_file = "/app/backend/server.py"
        if os.path.exists(backend_file):
            with open(backend_file, 'r') as f:
                content = f.read()
                
            if "async def initialize_database():" in content:
                print("✅ initialize_database() function found in server.py")
                
                # Check if it's being called
                if "asyncio.create_task(initialize_database())" in content:
                    print("✅ initialize_database() is being called on startup")
                    return True
                else:
                    print("❌ initialize_database() is NOT being called on startup")
                    print("   This could be the root cause of the seeding issue!")
                    return False
            else:
                print("❌ initialize_database() function not found in server.py")
                return False
        else:
            print("❌ Backend server.py file not found")
            return False

    def create_comprehensive_report(self):
        """Create a comprehensive report of findings"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE SEEDING INVESTIGATION REPORT")
        print("=" * 60)
        
        # Re-check database state for final report
        try:
            client = MongoClient(self.mongo_url)
            db = client[self.db_name]
            
            clinical_count = db.clinical_templates.count_documents({})
            notes_count = db.notes_templates.count_documents({})
            dispositions_count = db.dispositions.count_documents({})
            referral_sites_count = db.referral_sites.count_documents({})
            
            print(f"📋 FINAL DATABASE STATE:")
            print(f"   Clinical Templates: {clinical_count}")
            print(f"   Notes Templates: {notes_count}")
            print(f"   Dispositions: {dispositions_count}")
            print(f"   Referral Sites: {referral_sites_count}")
            
            if clinical_count == 0 and notes_count == 0 and dispositions_count == 0 and referral_sites_count == 0:
                print("\n🚨 CRITICAL FINDING: ALL SEEDED DATA IS MISSING!")
                print("   ROOT CAUSE: Seeding functions are not working or not being called")
                print("   IMPACT: Users lose all templates, dispositions, and referral sites on deployment")
                print("   URGENCY: IMMEDIATE FIX REQUIRED")
            elif any(count == 0 for count in [clinical_count, notes_count, dispositions_count, referral_sites_count]):
                print("\n⚠️  WARNING: PARTIAL SEEDING FAILURE DETECTED!")
                print("   Some seeded data collections are empty")
                print("   This indicates incomplete seeding process")
            else:
                print("\n✅ All seeded data collections contain data")
                print("   Seeding appears to be working correctly")
                
        except Exception as e:
            print(f"❌ Error generating final report: {str(e)}")

    def run_all_tests(self):
        """Run all seeding investigation tests"""
        print("🚨 STARTING CRITICAL SEEDING INVESTIGATION")
        print("=" * 60)
        
        # Run all tests
        tests = [
            ("1. Database State Check", self.check_database_state),
            ("2. API Endpoints Check", self.check_api_endpoints),
            ("3. Seeding Scripts Check", self.check_seeding_scripts),
            ("4. Manual Seeding Test", self.test_seeding_functions_manually),
            ("5. Backup System Check", self.check_backup_system),
            ("6. Server Startup Logs", self.check_server_startup_logs),
            ("7. Initialize Database Function", self.test_initialize_database_function)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
            
        # Generate comprehensive report
        self.create_comprehensive_report()
        
        print(f"\n📊 INVESTIGATION SUMMARY:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed < self.tests_run:
            print("\n🚨 CRITICAL ISSUES FOUND - IMMEDIATE ACTION REQUIRED")
        else:
            print("\n✅ All tests passed - Seeding system appears to be working")
            
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    # Load frontend environment to get backend URL
    load_dotenv('/app/frontend/.env')
    backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    
    print("🚨 CRITICAL SEEDING INVESTIGATION TEST")
    print("=" * 60)
    print("User Report: Templates, dispositions, and referral sites are not being")
    print("saved or imported into production. Users lose all data on deployment.")
    print("=" * 60)
    
    tester = SeedingInvestigationTester(backend_url)
    success = tester.run_all_tests()
    
    if not success:
        print("\n🚨 CRITICAL ISSUES DETECTED!")
        print("   The seeding system is not working properly.")
        print("   This confirms the user's report of data loss on deployment.")
        exit(1)
    else:
        print("\n✅ Seeding system appears to be working correctly.")
        exit(0)