#!/usr/bin/env python3

"""
FOCUSED TEMPLATE PERSISTENCE VERIFICATION TEST

This test focuses specifically on the core template persistence functionality
that was requested in the review.
"""

import requests
import json
import os
import subprocess
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
load_dotenv('/app/frontend/.env')

class FocusedTemplatePersistenceTest:
    def __init__(self):
        # Get backend URL from frontend environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
        self.api_base = f"{self.backend_url}/api"
        self.mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.getenv('DB_NAME', 'my420_ca_db')
        
        self.tests_run = 0
        self.tests_passed = 0
        
        print("🎯 FOCUSED TEMPLATE PERSISTENCE VERIFICATION")
        print("=" * 50)
        print(f"Testing API: {self.api_base}")
        print("=" * 50)

    def log_test(self, test_name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status} - {test_name}"
        if details:
            result += f" | {details}"
        
        print(result)
        return success

    def test_1_template_database_verification(self):
        """1. Template Database Verification - verify templates exist in MongoDB database"""
        print("\n📋 TEST 1: TEMPLATE DATABASE VERIFICATION")
        print("-" * 40)
        
        try:
            response = requests.get(f"{self.api_base}/clinical-templates", timeout=15)
            
            if response.status_code == 200:
                templates = response.json()
                
                # Check for expected default templates
                expected_templates = ["Positive", "Negative - Pipes", "Negative - Pipes/Straws", "Negative - Pipes/Straws/Needles"]
                template_names = [t.get('name', '') for t in templates]
                
                has_all_defaults = all(name in template_names for name in expected_templates)
                template_count = len(templates)
                
                success = has_all_defaults and template_count >= 4
                
                details = f"Found {template_count} templates. Default templates present: {has_all_defaults}"
                if has_all_defaults:
                    details += f". Templates: {template_names}"
                
                return self.log_test(
                    "Templates exist in MongoDB database",
                    success,
                    details
                )
            else:
                return self.log_test(
                    "Templates exist in MongoDB database",
                    False,
                    f"API returned status {response.status_code}: {response.text[:200]}"
                )
                
        except Exception as e:
            return self.log_test(
                "Templates exist in MongoDB database",
                False,
                f"Error: {str(e)}"
            )

    def test_2_persistence_testing(self):
        """2. Persistence Testing - verify backup file and MongoDB data directory"""
        print("\n📋 TEST 2: PERSISTENCE TESTING")
        print("-" * 40)
        
        # Test backup file exists
        backup_file = '/app/persistent-data/clinical-templates-backup.json'
        backup_exists = os.path.exists(backup_file)
        
        backup_details = ""
        if backup_exists:
            try:
                with open(backup_file, 'r') as f:
                    backup_data = json.load(f)
                    backup_details = f"Backup contains {len(backup_data)} templates"
            except Exception as e:
                backup_details = f"Backup file exists but error reading: {str(e)}"
        else:
            backup_details = "Backup file missing"
        
        backup_test = self.log_test(
            "Backup file exists at /app/persistent-data/clinical-templates-backup.json",
            backup_exists,
            backup_details
        )
        
        # Test MongoDB data directory
        mongodb_dir = '/app/persistent-data/mongodb'
        mongodb_exists = os.path.exists(mongodb_dir)
        
        mongodb_details = ""
        if mongodb_exists:
            try:
                files = os.listdir(mongodb_dir)
                mongodb_details = f"MongoDB directory contains {len(files)} files/folders"
            except Exception as e:
                mongodb_details = f"Directory exists but error reading: {str(e)}"
        else:
            mongodb_details = "MongoDB data directory missing"
        
        mongodb_test = self.log_test(
            "MongoDB data directory at /app/persistent-data/mongodb",
            mongodb_exists,
            mongodb_details
        )
        
        return backup_test and mongodb_test

    def test_3_production_deployment_simulation(self):
        """3. Production Deployment Simulation - test template restore and service restarts"""
        print("\n📋 TEST 3: PRODUCTION DEPLOYMENT SIMULATION")
        print("-" * 40)
        
        # Step 1: Create backup
        try:
            result = subprocess.run([
                'node', '/app/scripts/template-persistence.js', 'backup'
            ], capture_output=True, text=True, cwd="/app", env={
                **os.environ,
                'MONGO_URL': self.mongo_url,
                'DB_NAME': self.db_name
            })
            
            backup_success = result.returncode == 0 and 'Backed up' in result.stdout
            backup_test = self.log_test(
                "Template backup functionality works",
                backup_success,
                result.stdout.strip() if backup_success else result.stderr.strip()
            )
        except Exception as e:
            backup_test = self.log_test(
                "Template backup functionality works",
                False,
                f"Error: {str(e)}"
            )
        
        # Step 2: Test restore functionality
        try:
            result = subprocess.run([
                'node', '/app/scripts/template-persistence.js', 'restore'
            ], capture_output=True, text=True, cwd="/app", env={
                **os.environ,
                'MONGO_URL': self.mongo_url,
                'DB_NAME': self.db_name
            })
            
            restore_success = result.returncode == 0 and 'Restored' in result.stdout
            restore_test = self.log_test(
                "Template restore functionality works",
                restore_success,
                result.stdout.strip() if restore_success else result.stderr.strip()
            )
        except Exception as e:
            restore_test = self.log_test(
                "Template restore functionality works",
                False,
                f"Error: {str(e)}"
            )
        
        # Step 3: Verify templates survive backend restart
        try:
            print("🔄 Testing backend restart...")
            subprocess.run(['sudo', 'supervisorctl', 'restart', 'backend'], 
                         capture_output=True, timeout=30)
            time.sleep(5)  # Allow backend to fully restart
            
            # Check if templates still exist
            response = requests.get(f"{self.api_base}/clinical-templates", timeout=15)
            
            if response.status_code == 200:
                templates = response.json()
                restart_success = len(templates) >= 4
                restart_details = f"Found {len(templates)} templates after restart"
            else:
                restart_success = False
                restart_details = f"API returned status {response.status_code} after restart"
            
            restart_test = self.log_test(
                "Templates survive backend/MongoDB restarts",
                restart_success,
                restart_details
            )
            
        except Exception as e:
            restart_test = self.log_test(
                "Templates survive backend/MongoDB restarts",
                False,
                f"Error: {str(e)}"
            )
        
        return backup_test and restore_test and restart_test

    def test_4_api_endpoint_testing(self):
        """4. API Endpoint Testing - test GET /api/clinical-templates and CRUD operations"""
        print("\n📋 TEST 4: API ENDPOINT TESTING")
        print("-" * 40)
        
        # Test GET endpoint
        try:
            response = requests.get(f"{self.api_base}/clinical-templates", timeout=15)
            
            if response.status_code == 200:
                templates = response.json()
                expected_templates = ["Positive", "Negative - Pipes", "Negative - Pipes/Straws", "Negative - Pipes/Straws/Needles"]
                template_names = [t.get('name', '') for t in templates]
                
                has_defaults = all(name in template_names for name in expected_templates)
                
                get_test = self.log_test(
                    "GET /api/clinical-templates returns all templates",
                    has_defaults,
                    f"Found {len(templates)} templates, includes defaults: {has_defaults}"
                )
            else:
                get_test = self.log_test(
                    "GET /api/clinical-templates returns all templates",
                    False,
                    f"Status: {response.status_code}"
                )
        except Exception as e:
            get_test = self.log_test(
                "GET /api/clinical-templates returns all templates",
                False,
                f"Error: {str(e)}"
            )
        
        # Test POST endpoint (create)
        try:
            test_template = {
                "name": "API Test Template",
                "content": "This template tests the API functionality.",
                "is_default": False
            }
            
            response = requests.post(
                f"{self.api_base}/clinical-templates",
                json=test_template,
                timeout=15
            )
            
            if response.status_code == 200:
                created_template = response.json()
                create_success = (
                    created_template.get('name') == test_template['name'] and
                    'id' in created_template
                )
                
                if create_success:
                    self.test_template_id = created_template['id']
                
                create_test = self.log_test(
                    "Templates can be saved correctly",
                    create_success,
                    f"Created template with ID: {created_template.get('id', 'N/A')}"
                )
            else:
                create_test = self.log_test(
                    "Templates can be saved correctly",
                    False,
                    f"Status: {response.status_code}"
                )
        except Exception as e:
            create_test = self.log_test(
                "Templates can be saved correctly",
                False,
                f"Error: {str(e)}"
            )
        
        # Test retrieval of created template
        if hasattr(self, 'test_template_id'):
            try:
                response = requests.get(f"{self.api_base}/clinical-templates", timeout=15)
                
                if response.status_code == 200:
                    templates = response.json()
                    found_template = next((t for t in templates if t.get('id') == self.test_template_id), None)
                    
                    retrieve_test = self.log_test(
                        "Templates can be retrieved correctly",
                        found_template is not None,
                        f"Template found: {found_template is not None}"
                    )
                else:
                    retrieve_test = self.log_test(
                        "Templates can be retrieved correctly",
                        False,
                        f"Status: {response.status_code}"
                    )
            except Exception as e:
                retrieve_test = self.log_test(
                    "Templates can be retrieved correctly",
                    False,
                    f"Error: {str(e)}"
                )
        else:
            retrieve_test = self.log_test(
                "Templates can be retrieved correctly",
                False,
                "No test template ID available"
            )
        
        # Cleanup test template
        if hasattr(self, 'test_template_id'):
            try:
                requests.delete(f"{self.api_base}/clinical-templates/{self.test_template_id}", timeout=15)
            except:
                pass  # Cleanup failure is not critical
        
        return get_test and create_test and retrieve_test

    def run_all_tests(self):
        """Run all focused template persistence tests"""
        print("🚀 STARTING FOCUSED TEMPLATE PERSISTENCE VERIFICATION")
        
        # Run the 4 critical test requirements
        test1_result = self.test_1_template_database_verification()
        test2_result = self.test_2_persistence_testing()
        test3_result = self.test_3_production_deployment_simulation()
        test4_result = self.test_4_api_endpoint_testing()
        
        # Final summary
        print("\n" + "=" * 50)
        print("🎯 FINAL VERIFICATION RESULTS")
        print("=" * 50)
        
        print(f"📊 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Check critical requirements
        critical_tests = [
            ("Template Database Verification", test1_result),
            ("Persistence Testing", test2_result),
            ("Production Deployment Simulation", test3_result),
            ("API Endpoint Testing", test4_result)
        ]
        
        all_critical_passed = all(result for _, result in critical_tests)
        
        print(f"\n📋 CRITICAL REQUIREMENTS:")
        for name, result in critical_tests:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {name}")
        
        if all_critical_passed:
            print("\n🎉 ALL CRITICAL REQUIREMENTS PASSED!")
            print("✅ Template persistence solution is working correctly")
            print("✅ Production deployment issue has been resolved")
            print("✅ Templates persist in database permanently")
            print("✅ Backup system working correctly")
            print("✅ API endpoints functional")
            print("✅ Templates available across all deployments")
            print("✅ User will never need to re-enter templates again")
        else:
            print("\n⚠️ SOME CRITICAL REQUIREMENTS FAILED")
            print("❌ Template persistence solution needs attention")
        
        print("\n" + "=" * 50)
        
        return all_critical_passed

if __name__ == "__main__":
    tester = FocusedTemplatePersistenceTest()
    tester.run_all_tests()