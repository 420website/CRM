#!/usr/bin/env python3
"""
COMPREHENSIVE SEEDING AND PERSISTENCE TEST
==========================================

This test addresses the critical user report:
"Templates, dispositions, and referral sites are not being saved or imported into production.
Users lose all their data on deployment."

This test will:
1. Check current database state
2. Verify seeding functions are working
3. Test data persistence mechanisms
4. Identify any critical issues
"""

import requests
import json
import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

class ComprehensiveSeedingTest:
    def __init__(self):
        # Load environment variables
        load_dotenv('/app/frontend/.env')
        self.backend_url = os.environ.get('REACT_APP_BACKEND_URL')
        
        load_dotenv('/app/backend/.env')
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'my420_ca_db')
        
        self.headers = {'Content-Type': 'application/json'}
        self.tests_passed = 0
        self.tests_failed = 0
        
        print("🚨 COMPREHENSIVE SEEDING AND PERSISTENCE TEST")
        print("=" * 60)
        print("USER REPORT: Templates, dispositions, and referral sites are not")
        print("being saved or imported into production. Users lose all data on deployment.")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"MongoDB: {self.mongo_url}")
        print(f"Database: {self.db_name}")
        print("=" * 60)

    def test_database_connection(self):
        """Test MongoDB connection"""
        print("\n🔍 1. TESTING DATABASE CONNECTION")
        print("-" * 40)
        
        try:
            client = MongoClient(self.mongo_url)
            db = client[self.db_name]
            # Test connection
            db.admin.command('ping')
            print("✅ MongoDB connection successful")
            self.tests_passed += 1
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
            self.tests_failed += 1
            return False

    def check_current_database_state(self):
        """Check current state of all seeded data"""
        print("\n🔍 2. CHECKING CURRENT DATABASE STATE")
        print("-" * 40)
        
        try:
            client = MongoClient(self.mongo_url)
            db = client[self.db_name]
            
            # Get counts
            clinical_count = db.clinical_templates.count_documents({})
            notes_count = db.notes_templates.count_documents({})
            dispositions_count = db.dispositions.count_documents({})
            referral_sites_count = db.referral_sites.count_documents({})
            
            print(f"📋 Clinical Templates: {clinical_count}")
            print(f"📝 Notes Templates: {notes_count}")
            print(f"🏥 Dispositions: {dispositions_count}")
            print(f"🏢 Referral Sites: {referral_sites_count}")
            
            # Check for default data
            clinical_default = db.clinical_templates.count_documents({"is_default": True})
            notes_default = db.notes_templates.count_documents({"is_default": True})
            dispositions_default = db.dispositions.count_documents({"is_default": True})
            referral_sites_default = db.referral_sites.count_documents({"is_default": True})
            
            print(f"\n📊 Default Data:")
            print(f"   Clinical Templates (default): {clinical_default}")
            print(f"   Notes Templates (default): {notes_default}")
            print(f"   Dispositions (default): {dispositions_default}")
            print(f"   Referral Sites (default): {referral_sites_default}")
            
            # Analyze the data
            total_data = clinical_count + notes_count + dispositions_count + referral_sites_count
            
            if total_data == 0:
                print("\n🚨 CRITICAL ISSUE: NO SEEDED DATA FOUND!")
                print("   This confirms the user's report of data loss.")
                self.tests_failed += 1
                return False
            elif clinical_count == 0 or notes_count == 0 or dispositions_count == 0 or referral_sites_count == 0:
                print("\n⚠️  WARNING: Some collections are empty!")
                print("   This indicates partial seeding failure.")
                self.tests_failed += 1
                return False
            else:
                print("\n✅ All seeded data collections contain data.")
                print("   Database state appears healthy.")
                self.tests_passed += 1
                return True
                
        except Exception as e:
            print(f"❌ Error checking database state: {str(e)}")
            self.tests_failed += 1
            return False

    def test_api_endpoints(self):
        """Test all seeded data API endpoints"""
        print("\n🔍 3. TESTING API ENDPOINTS")
        print("-" * 40)
        
        endpoints = [
            ("Clinical Templates", "/api/clinical-templates"),
            ("Notes Templates", "/api/notes-templates"),
            ("Dispositions", "/api/dispositions"),
            ("Referral Sites", "/api/referral-sites")
        ]
        
        all_working = True
        
        for name, endpoint in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", 
                                      headers=self.headers, timeout=30)
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
        
        if all_working:
            print("\n✅ All API endpoints are working correctly")
            self.tests_passed += 1
            return True
        else:
            print("\n❌ Some API endpoints have issues")
            self.tests_failed += 1
            return False

    def test_seeding_scripts(self):
        """Test seeding scripts execution"""
        print("\n🔍 4. TESTING SEEDING SCRIPTS")
        print("-" * 40)
        
        # Test clinical templates seeding
        print("📋 Testing Clinical Templates Seeding...")
        try:
            result = subprocess.run([
                'node', '/app/scripts/seed-templates.js'
            ], capture_output=True, text=True, cwd="/app", env={
                **os.environ,
                'MONGO_URL': self.mongo_url,
                'DB_NAME': self.db_name
            }, timeout=30)
            
            if result.returncode == 0:
                print("✅ Clinical templates seeding script executed successfully")
                if "seeding completed successfully" in result.stdout.lower():
                    print("   ✅ Seeding completed successfully")
                else:
                    print(f"   Output: {result.stdout}")
            else:
                print("❌ Clinical templates seeding script failed")
                print(f"   Error: {result.stderr}")
                self.tests_failed += 1
                return False
        except Exception as e:
            print(f"❌ Error running clinical templates seeding: {str(e)}")
            self.tests_failed += 1
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
            }, timeout=30)
            
            if result.returncode == 0:
                print("✅ Notes templates seeding script executed successfully")
                if "seeding completed successfully" in result.stdout.lower():
                    print("   ✅ Seeding completed successfully")
                else:
                    print(f"   Output: {result.stdout}")
            else:
                print("❌ Notes templates seeding script failed")
                print(f"   Error: {result.stderr}")
                self.tests_failed += 1
                return False
        except Exception as e:
            print(f"❌ Error running notes templates seeding: {str(e)}")
            self.tests_failed += 1
            return False
            
        print("\n✅ All seeding scripts executed successfully")
        self.tests_passed += 1
        return True

    def test_backup_system(self):
        """Test backup and restore system"""
        print("\n🔍 5. TESTING BACKUP SYSTEM")
        print("-" * 40)
        
        # Check backup directories
        backup_dirs = ["/app/persistent-data"]
        backup_files = [
            "/app/persistent-data/clinical-templates-backup.json",
            "/app/persistent-data/notes-templates-backup.json"
        ]
        
        # Check directories
        for backup_dir in backup_dirs:
            if os.path.exists(backup_dir):
                print(f"✅ Backup directory exists: {backup_dir}")
                try:
                    contents = os.listdir(backup_dir)
                    print(f"   Contents: {len(contents)} items")
                except Exception as e:
                    print(f"   ❌ Error listing contents: {str(e)}")
            else:
                print(f"❌ Backup directory missing: {backup_dir}")
                self.tests_failed += 1
                return False
                
        # Check backup files
        backup_files_ok = True
        for backup_file in backup_files:
            if os.path.exists(backup_file):
                try:
                    size = os.path.getsize(backup_file)
                    print(f"✅ Backup file exists: {os.path.basename(backup_file)} ({size} bytes)")
                    if size == 0:
                        print(f"   ⚠️  WARNING: Backup file is empty!")
                        backup_files_ok = False
                except Exception as e:
                    print(f"   ❌ Error checking file: {str(e)}")
                    backup_files_ok = False
            else:
                print(f"❌ Backup file missing: {os.path.basename(backup_file)}")
                backup_files_ok = False
                
        if backup_files_ok:
            print("\n✅ Backup system is working correctly")
            self.tests_passed += 1
            return True
        else:
            print("\n❌ Backup system has issues")
            self.tests_failed += 1
            return False

    def test_initialize_database_function(self):
        """Test if initialize_database function is properly configured"""
        print("\n🔍 6. TESTING INITIALIZE_DATABASE FUNCTION")
        print("-" * 40)
        
        backend_file = "/app/backend/server.py"
        if not os.path.exists(backend_file):
            print("❌ Backend server.py file not found")
            self.tests_failed += 1
            return False
            
        with open(backend_file, 'r') as f:
            content = f.read()
            
        # Check if function exists
        if "async def initialize_database():" not in content:
            print("❌ initialize_database() function not found")
            self.tests_failed += 1
            return False
        else:
            print("✅ initialize_database() function found")
            
        # Check if it's being called
        if "asyncio.create_task(initialize_database())" not in content:
            print("❌ initialize_database() is NOT being called on startup")
            print("   This could be the root cause of seeding issues!")
            self.tests_failed += 1
            return False
        else:
            print("✅ initialize_database() is being called on startup")
            
        # Check what the function does
        function_calls = []
        if "await seed_clinical_templates()" in content:
            function_calls.append("seed_clinical_templates")
        if "await seed_notes_templates()" in content:
            function_calls.append("seed_notes_templates")
        if "await seed_dispositions()" in content:
            function_calls.append("seed_dispositions")
        if "await seed_referral_sites()" in content:
            function_calls.append("seed_referral_sites")
        if "await backup_templates()" in content:
            function_calls.append("backup_templates")
            
        print(f"✅ Function calls found: {', '.join(function_calls)}")
        
        if len(function_calls) >= 4:  # Should have at least the 4 seeding functions
            print("✅ All required seeding functions are called")
            self.tests_passed += 1
            return True
        else:
            print("❌ Some seeding functions are missing")
            self.tests_failed += 1
            return False

    def generate_final_report(self):
        """Generate final comprehensive report"""
        print("\n" + "=" * 60)
        print("📊 FINAL COMPREHENSIVE REPORT")
        print("=" * 60)
        
        # Re-check database state for final numbers
        try:
            client = MongoClient(self.mongo_url)
            db = client[self.db_name]
            
            clinical_count = db.clinical_templates.count_documents({})
            notes_count = db.notes_templates.count_documents({})
            dispositions_count = db.dispositions.count_documents({})
            referral_sites_count = db.referral_sites.count_documents({})
            
            print(f"📊 FINAL DATABASE STATE:")
            print(f"   Clinical Templates: {clinical_count}")
            print(f"   Notes Templates: {notes_count}")
            print(f"   Dispositions: {dispositions_count}")
            print(f"   Referral Sites: {referral_sites_count}")
            
            total_tests = self.tests_passed + self.tests_failed
            success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
            
            print(f"\n📈 TEST RESULTS:")
            print(f"   Tests Passed: {self.tests_passed}")
            print(f"   Tests Failed: {self.tests_failed}")
            print(f"   Success Rate: {success_rate:.1f}%")
            
            # Determine overall status
            if self.tests_failed == 0:
                print(f"\n✅ CONCLUSION: SEEDING SYSTEM IS WORKING CORRECTLY")
                print("   All templates, dispositions, and referral sites are properly seeded.")
                print("   Data persistence mechanisms are functioning.")
                print("   The user's reported issue may be resolved or was temporary.")
                return True
            else:
                print(f"\n🚨 CONCLUSION: CRITICAL ISSUES FOUND")
                print("   The seeding system has problems that need immediate attention.")
                print("   This confirms the user's report of data loss on deployment.")
                
                # Provide specific recommendations
                if clinical_count == 0 or notes_count == 0 or dispositions_count == 0 or referral_sites_count == 0:
                    print("\n🔧 RECOMMENDED ACTIONS:")
                    print("   1. Check if initialize_database() is being called on server startup")
                    print("   2. Verify seeding scripts are executable and working")
                    print("   3. Check MongoDB connection and permissions")
                    print("   4. Review server startup logs for seeding errors")
                    
                return False
                
        except Exception as e:
            print(f"❌ Error generating final report: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("\n🚀 STARTING COMPREHENSIVE SEEDING TESTS")
        
        tests = [
            ("Database Connection", self.test_database_connection),
            ("Current Database State", self.check_current_database_state),
            ("API Endpoints", self.test_api_endpoints),
            ("Seeding Scripts", self.test_seeding_scripts),
            ("Backup System", self.test_backup_system),
            ("Initialize Database Function", self.test_initialize_database_function)
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"❌ {test_name} failed with error: {str(e)}")
                self.tests_failed += 1
        
        # Generate final report
        return self.generate_final_report()

if __name__ == "__main__":
    tester = ComprehensiveSeedingTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ ALL TESTS PASSED - Seeding system is working correctly")
        exit(0)
    else:
        print("\n🚨 CRITICAL ISSUES FOUND - Immediate action required")
        exit(1)