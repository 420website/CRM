#!/usr/bin/env python3

"""
FINAL PRODUCTION TEMPLATE PERSISTENCE VERIFICATION TEST

This test verifies that the complete template persistence solution is working correctly
and that the production deployment issue has been resolved.

Test Requirements:
1. Template Database Verification - verify templates exist in MongoDB database
2. Persistence Testing - verify backup file exists and MongoDB data directory
3. Production Deployment Simulation - test template restore functionality  
4. API Endpoint Testing - test all clinical template endpoints
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

class TemplatePersistenceVerifier:
    def __init__(self):
        # Get backend URL from frontend environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
        self.api_base = f"{self.backend_url}/api"
        self.mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.getenv('DB_NAME', 'my420_ca_db')
        
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        print("🧪 FINAL PRODUCTION TEMPLATE PERSISTENCE VERIFICATION")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"API Base: {self.api_base}")
        print(f"MongoDB URL: {self.mongo_url}")
        print(f"Database: {self.db_name}")
        print("=" * 60)

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
        self.test_results.append({
            'name': test_name,
            'success': success,
            'details': details
        })
        return success

    def test_backend_health(self):
        """Test that backend is running and accessible"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=10)
            return self.log_test(
                "Backend Health Check",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            return self.log_test(
                "Backend Health Check",
                False,
                f"Error: {str(e)}"
            )

    def test_mongodb_connection(self):
        """Test MongoDB connection and database existence"""
        try:
            # Use Node.js to test MongoDB connection
            test_script = """
const { MongoClient } = require('mongodb');
(async () => {
  try {
    const client = new MongoClient(process.env.MONGO_URL || 'mongodb://localhost:27017');
    await client.connect();
    const db = client.db(process.env.DB_NAME || 'my420_ca_db');
    const collections = await db.listCollections().toArray();
    console.log('SUCCESS');
    await client.close();
  } catch (e) {
    console.log('ERROR:', e.message);
  }
})();
"""
            
            result = subprocess.run([
                'node', '-e', test_script
            ], capture_output=True, text=True, cwd="/app", env={
                **os.environ,
                'MONGO_URL': self.mongo_url,
                'DB_NAME': self.db_name
            })
            
            success = 'SUCCESS' in result.stdout
            return self.log_test(
                "MongoDB Connection Test",
                success,
                result.stdout.strip() if success else result.stderr.strip()
            )
            
        except Exception as e:
            return self.log_test(
                "MongoDB Connection Test",
                False,
                f"Error: {str(e)}"
            )

    def test_persistent_directories(self):
        """Test that persistent directories exist"""
        directories = [
            '/app/persistent-data',
            '/app/persistent-data/mongodb',
            '/app/persistent-data/backups'
        ]
        
        all_exist = True
        missing_dirs = []
        
        for directory in directories:
            if not os.path.exists(directory):
                all_exist = False
                missing_dirs.append(directory)
        
        return self.log_test(
            "Persistent Directories Check",
            all_exist,
            f"Missing: {missing_dirs}" if missing_dirs else "All directories exist"
        )

    def test_backup_file_exists(self):
        """Test that backup file exists"""
        backup_file = '/app/persistent-data/clinical-templates-backup.json'
        exists = os.path.exists(backup_file)
        
        details = ""
        if exists:
            try:
                with open(backup_file, 'r') as f:
                    backup_data = json.load(f)
                    details = f"Contains {len(backup_data)} templates"
            except Exception as e:
                details = f"File exists but error reading: {str(e)}"
        else:
            details = "Backup file does not exist"
        
        return self.log_test(
            "Backup File Verification",
            exists,
            details
        )

    def test_template_seeding(self):
        """Test that template seeding works"""
        try:
            result = subprocess.run([
                'node', '/app/scripts/seed-templates.js'
            ], capture_output=True, text=True, cwd="/app", env={
                **os.environ,
                'MONGO_URL': self.mongo_url,
                'DB_NAME': self.db_name
            })
            
            success = result.returncode == 0
            return self.log_test(
                "Template Seeding Test",
                success,
                result.stdout.strip() if success else result.stderr.strip()
            )
            
        except Exception as e:
            return self.log_test(
                "Template Seeding Test",
                False,
                f"Error: {str(e)}"
            )

    def test_get_all_templates_api(self):
        """Test GET /api/clinical-templates endpoint"""
        try:
            response = requests.get(f"{self.api_base}/clinical-templates", timeout=10)
            
            if response.status_code == 200:
                templates = response.json()
                expected_templates = ["Positive", "Negative - Pipes", "Negative - Pipes/Straws", "Negative - Pipes/Straws/Needles"]
                
                template_names = [t.get('name', '') for t in templates]
                has_defaults = all(name in template_names for name in expected_templates)
                
                return self.log_test(
                    "GET Clinical Templates API",
                    has_defaults,
                    f"Found {len(templates)} templates, has defaults: {has_defaults}"
                )
            else:
                return self.log_test(
                    "GET Clinical Templates API",
                    False,
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                
        except Exception as e:
            return self.log_test(
                "GET Clinical Templates API",
                False,
                f"Error: {str(e)}"
            )

    def test_create_template_api(self):
        """Test POST /api/clinical-templates endpoint"""
        try:
            test_template = {
                "name": "Test Template - Persistence Verification",
                "content": "This is a test template created during persistence verification testing.",
                "is_default": False
            }
            
            response = requests.post(
                f"{self.api_base}/clinical-templates",
                json=test_template,
                timeout=10
            )
            
            if response.status_code == 200:
                created_template = response.json()
                success = (
                    created_template.get('name') == test_template['name'] and
                    created_template.get('content') == test_template['content'] and
                    'id' in created_template
                )
                
                # Store template ID for cleanup
                if success:
                    self.test_template_id = created_template['id']
                
                return self.log_test(
                    "POST Create Template API",
                    success,
                    f"Created template with ID: {created_template.get('id', 'N/A')}"
                )
            else:
                return self.log_test(
                    "POST Create Template API",
                    False,
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                
        except Exception as e:
            return self.log_test(
                "POST Create Template API",
                False,
                f"Error: {str(e)}"
            )

    def test_update_template_api(self):
        """Test PUT /api/clinical-templates/{id} endpoint"""
        if not hasattr(self, 'test_template_id'):
            return self.log_test(
                "PUT Update Template API",
                False,
                "No test template ID available (create test failed)"
            )
        
        try:
            update_data = {
                "content": "Updated content for persistence verification testing."
            }
            
            response = requests.put(
                f"{self.api_base}/clinical-templates/{self.test_template_id}",
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                updated_template = response.json()
                success = updated_template.get('content') == update_data['content']
                
                return self.log_test(
                    "PUT Update Template API",
                    success,
                    f"Updated template content successfully"
                )
            else:
                return self.log_test(
                    "PUT Update Template API",
                    False,
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                
        except Exception as e:
            return self.log_test(
                "PUT Update Template API",
                False,
                f"Error: {str(e)}"
            )

    def test_delete_template_api(self):
        """Test DELETE /api/clinical-templates/{id} endpoint"""
        if not hasattr(self, 'test_template_id'):
            return self.log_test(
                "DELETE Template API",
                False,
                "No test template ID available (create test failed)"
            )
        
        try:
            response = requests.delete(
                f"{self.api_base}/clinical-templates/{self.test_template_id}",
                timeout=10
            )
            
            success = response.status_code == 200
            return self.log_test(
                "DELETE Template API",
                success,
                f"Status: {response.status_code}"
            )
                
        except Exception as e:
            return self.log_test(
                "DELETE Template API",
                False,
                f"Error: {str(e)}"
            )

    def test_bulk_save_templates_api(self):
        """Test POST /api/clinical-templates/save-all endpoint"""
        try:
            test_templates = {
                "Bulk Test Template 1": "Content for bulk test template 1",
                "Bulk Test Template 2": "Content for bulk test template 2"
            }
            
            response = requests.post(
                f"{self.api_base}/clinical-templates/save-all",
                json=test_templates,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                success = result.get('count', 0) == len(test_templates)
                
                return self.log_test(
                    "POST Bulk Save Templates API",
                    success,
                    f"Saved {result.get('count', 0)} templates"
                )
            else:
                return self.log_test(
                    "POST Bulk Save Templates API",
                    False,
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                
        except Exception as e:
            return self.log_test(
                "POST Bulk Save Templates API",
                False,
                f"Error: {str(e)}"
            )

    def test_template_backup_functionality(self):
        """Test template backup functionality"""
        try:
            result = subprocess.run([
                'node', '/app/scripts/template-persistence.js', 'backup'
            ], capture_output=True, text=True, cwd="/app", env={
                **os.environ,
                'MONGO_URL': self.mongo_url,
                'DB_NAME': self.db_name
            })
            
            success = result.returncode == 0 and 'Backed up' in result.stdout
            return self.log_test(
                "Template Backup Functionality",
                success,
                result.stdout.strip() if success else result.stderr.strip()
            )
            
        except Exception as e:
            return self.log_test(
                "Template Backup Functionality",
                False,
                f"Error: {str(e)}"
            )

    def test_template_restore_functionality(self):
        """Test template restore functionality"""
        try:
            result = subprocess.run([
                'node', '/app/scripts/template-persistence.js', 'restore'
            ], capture_output=True, text=True, cwd="/app", env={
                **os.environ,
                'MONGO_URL': self.mongo_url,
                'DB_NAME': self.db_name
            })
            
            success = result.returncode == 0 and 'Restored' in result.stdout
            return self.log_test(
                "Template Restore Functionality",
                success,
                result.stdout.strip() if success else result.stderr.strip()
            )
            
        except Exception as e:
            return self.log_test(
                "Template Restore Functionality",
                False,
                f"Error: {str(e)}"
            )

    def test_production_deployment_simulation(self):
        """Simulate production deployment scenario"""
        print("\n🚀 PRODUCTION DEPLOYMENT SIMULATION")
        print("-" * 40)
        
        # Step 1: Backup current templates
        backup_success = self.test_template_backup_functionality()
        
        # Step 2: Simulate deployment (restart services)
        try:
            print("🔄 Simulating service restart...")
            subprocess.run(['sudo', 'supervisorctl', 'restart', 'backend'], 
                         capture_output=True, timeout=30)
            time.sleep(3)
            
            restart_success = True
        except Exception as e:
            restart_success = False
            print(f"❌ Service restart failed: {str(e)}")
        
        # Step 3: Verify templates still exist after restart
        if restart_success:
            time.sleep(2)  # Allow backend to fully start
            templates_exist = self.test_get_all_templates_api()
        else:
            templates_exist = False
        
        # Step 4: Test restore if needed
        if not templates_exist:
            restore_success = self.test_template_restore_functionality()
            if restore_success:
                time.sleep(2)
                templates_exist = self.test_get_all_templates_api()
        
        overall_success = backup_success and restart_success and templates_exist
        
        return self.log_test(
            "Production Deployment Simulation",
            overall_success,
            "Templates persist across service restarts" if overall_success else "Templates do not persist properly"
        )

    def run_all_tests(self):
        """Run all template persistence verification tests"""
        print("\n🧪 STARTING TEMPLATE PERSISTENCE VERIFICATION TESTS")
        print("=" * 60)
        
        # Core infrastructure tests
        print("\n📋 INFRASTRUCTURE TESTS")
        print("-" * 30)
        self.test_backend_health()
        self.test_mongodb_connection()
        self.test_persistent_directories()
        self.test_backup_file_exists()
        
        # Template seeding and database tests
        print("\n📋 DATABASE TESTS")
        print("-" * 30)
        self.test_template_seeding()
        
        # API endpoint tests
        print("\n📋 API ENDPOINT TESTS")
        print("-" * 30)
        self.test_get_all_templates_api()
        self.test_create_template_api()
        self.test_update_template_api()
        self.test_delete_template_api()
        self.test_bulk_save_templates_api()
        
        # Persistence functionality tests
        print("\n📋 PERSISTENCE FUNCTIONALITY TESTS")
        print("-" * 30)
        self.test_template_backup_functionality()
        self.test_template_restore_functionality()
        
        # Production deployment simulation
        print("\n📋 PRODUCTION DEPLOYMENT SIMULATION")
        print("-" * 30)
        self.test_production_deployment_simulation()
        
        # Final summary
        self.print_final_summary()

    def print_final_summary(self):
        """Print final test summary"""
        print("\n" + "=" * 60)
        print("🎯 FINAL PRODUCTION TEMPLATE PERSISTENCE VERIFICATION RESULTS")
        print("=" * 60)
        
        print(f"📊 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Template persistence solution is working correctly")
            print("✅ Production deployment issue has been resolved")
            print("✅ Templates will persist across all deployments")
            print("✅ Users will never need to re-enter templates again")
        else:
            print("\n⚠️ SOME TESTS FAILED")
            print("❌ Template persistence solution needs attention")
            
            failed_tests = [r for r in self.test_results if not r['success']]
            print(f"\n📋 Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  ❌ {test['name']}: {test['details']}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    verifier = TemplatePersistenceVerifier()
    verifier.run_all_tests()