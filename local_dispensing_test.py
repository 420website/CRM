import requests
import unittest
import json
from datetime import datetime, date
import random
import string
import sys
import os
from dotenv import load_dotenv

# Use localhost for testing
BACKEND_URL = "http://localhost:8001"

class DispensingAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.registration_id = None
        self.dispensing_ids = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if not headers:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    # Check for proper error format if this is an error response
                    if expected_status >= 400 and 'detail' in response_data:
                        print(f"✅ Error message format correct: {response_data['detail']}")
                    return success, response_data
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"Response: {response_data}")
                    # Check if error response has proper format
                    if response.status_code >= 400 and 'detail' in response_data:
                        print(f"✅ Error message format correct: {response_data['detail']}")
                    elif response.status_code >= 400:
                        print("❌ Error response missing 'detail' field")
                    return False, response_data
                except:
                    print(f"Response: {response.text}")
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def generate_test_data(self):
        """Generate random test data for admin registration"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        admin_registration = {
            "firstName": f"Test {random_suffix}",
            "lastName": f"User {random_suffix}",
            "patientConsent": "Verbal",
            "gender": "Male",
            "province": "Ontario"
        }
        
        return admin_registration

    def create_test_registration(self):
        """Create a test registration to use for dispensing tests"""
        print("\n🔍 Creating test registration for dispensing tests...")
        
        admin_registration = self.generate_test_data()
        
        success, response = self.run_test(
            "Create Admin Registration",
            "POST",
            "api/admin-register",
            200,
            data=admin_registration
        )
        
        if success and 'registration_id' in response:
            self.registration_id = response['registration_id']
            print(f"✅ Created test registration with ID: {self.registration_id}")
            return True
        else:
            print("❌ Failed to create test registration")
            return False

    def test_create_dispensing(self, data=None):
        """Test creating a new dispensing record"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        if not data:
            data = {
                "medication": "Ecplusa",
                "rx": "RX12345",
                "quantity": "28",
                "lot": "LOT123",
                "product_type": "Commercial",
                "expiry_date": "2025-12-31"
            }
        
        success, response = self.run_test(
            "Create Dispensing Record",
            "POST",
            f"api/admin-registration/{self.registration_id}/dispensing",
            200,
            data=data
        )
        
        if success and 'dispensing_id' in response:
            dispensing_id = response['dispensing_id']
            self.dispensing_ids.append(dispensing_id)
            print(f"✅ Created dispensing record with ID: {dispensing_id}")
            return True, dispensing_id
        else:
            print("❌ Failed to create dispensing record")
            return False, None

    def test_get_dispensing(self):
        """Test getting all dispensing records for a registration"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        # Create a dispensing record if none exists
        if not self.dispensing_ids:
            self.test_create_dispensing()
        
        success, response = self.run_test(
            "Get Dispensing Records",
            "GET",
            f"api/admin-registration/{self.registration_id}/dispensing",
            200
        )
        
        if success and 'dispensing' in response:
            dispensing_records = response['dispensing']
            print(f"✅ Retrieved {len(dispensing_records)} dispensing records")
            
            # Verify the records are sorted by created_at (newest first)
            if len(dispensing_records) > 1:
                is_sorted = all(
                    dispensing_records[i]['created_at'] >= dispensing_records[i+1]['created_at']
                    for i in range(len(dispensing_records)-1)
                )
                if is_sorted:
                    print("✅ Dispensing records are correctly sorted by created_at (newest first)")
                else:
                    print("❌ Dispensing records are NOT sorted by created_at (newest first)")
            
            return True, dispensing_records
        else:
            print("❌ Failed to retrieve dispensing records")
            return False, []

    def test_update_dispensing(self):
        """Test updating an existing dispensing record"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        # Create a dispensing record if none exists
        if not self.dispensing_ids:
            success, dispensing_id = self.test_create_dispensing()
            if not success:
                return False, {}
        else:
            dispensing_id = self.dispensing_ids[0]
        
        update_data = {
            "medication": "Maviret",
            "rx": "RX67890",
            "quantity": "56",
            "lot": "LOT456",
            "product_type": "Compassionate",
            "expiry_date": "2026-06-30"
        }
        
        success, response = self.run_test(
            "Update Dispensing Record",
            "PUT",
            f"api/admin-registration/{self.registration_id}/dispensing/{dispensing_id}",
            200,
            data=update_data
        )
        
        if success:
            print(f"✅ Updated dispensing record with ID: {dispensing_id}")
            
            # Verify the update by getting the record
            get_success, get_response = self.run_test(
                "Verify Dispensing Update",
                "GET",
                f"api/admin-registration/{self.registration_id}/dispensing",
                200
            )
            
            if get_success and 'dispensing' in get_response:
                updated_record = next((r for r in get_response['dispensing'] if r['id'] == dispensing_id), None)
                if updated_record:
                    all_fields_updated = all(
                        updated_record[key] == update_data[key]
                        for key in update_data
                    )
                    if all_fields_updated:
                        print("✅ All fields were correctly updated")
                    else:
                        print("❌ Not all fields were correctly updated")
                        for key in update_data:
                            if key in updated_record and updated_record[key] != update_data[key]:
                                print(f"  - Field '{key}': expected '{update_data[key]}', got '{updated_record[key]}'")
                else:
                    print("❌ Could not find the updated record")
            
            return True, response
        else:
            print("❌ Failed to update dispensing record")
            return False, {}

    def test_delete_dispensing(self):
        """Test deleting a dispensing record"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        # Create a dispensing record if none exists
        if not self.dispensing_ids:
            success, dispensing_id = self.test_create_dispensing()
            if not success:
                return False, {}
        else:
            dispensing_id = self.dispensing_ids[0]
        
        success, response = self.run_test(
            "Delete Dispensing Record",
            "DELETE",
            f"api/admin-registration/{self.registration_id}/dispensing/{dispensing_id}",
            200
        )
        
        if success:
            print(f"✅ Deleted dispensing record with ID: {dispensing_id}")
            
            # Remove the ID from our list
            if dispensing_id in self.dispensing_ids:
                self.dispensing_ids.remove(dispensing_id)
            
            # Verify the deletion by getting all records
            get_success, get_response = self.run_test(
                "Verify Dispensing Deletion",
                "GET",
                f"api/admin-registration/{self.registration_id}/dispensing",
                200
            )
            
            if get_success and 'dispensing' in get_response:
                deleted_record = next((r for r in get_response['dispensing'] if r['id'] == dispensing_id), None)
                if deleted_record:
                    print("❌ Record was not actually deleted")
                else:
                    print("✅ Record was successfully deleted")
            
            return True, response
        else:
            print("❌ Failed to delete dispensing record")
            return False, {}

    def test_dispensing_validation(self):
        """Test validation for dispensing records"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        print("\n🔍 Testing Dispensing Validation...")
        
        # Test 1: Missing required field (medication)
        invalid_data = {
            "rx": "RX12345",
            "quantity": "28",
            "lot": "LOT123",
            "product_type": "Commercial",
            "expiry_date": "2025-12-31"
        }
        
        success, response = self.run_test(
            "Dispensing - Missing Required Field (medication)",
            "POST",
            f"api/admin-registration/{self.registration_id}/dispensing",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test 2: Invalid registration ID
        invalid_reg_id = "nonexistent-id"
        valid_data = {
            "medication": "Ecplusa",
            "rx": "RX12345",
            "quantity": "28",
            "lot": "LOT123",
            "product_type": "Commercial",
            "expiry_date": "2025-12-31"
        }
        
        success, response = self.run_test(
            "Dispensing - Invalid Registration ID",
            "POST",
            f"api/admin-registration/{invalid_reg_id}/dispensing",
            404,  # Not found status code
            data=valid_data
        )
        
        # Test 3: Invalid dispensing ID for update
        invalid_dispensing_id = "nonexistent-id"
        
        success, response = self.run_test(
            "Dispensing - Invalid Dispensing ID for Update",
            "PUT",
            f"api/admin-registration/{self.registration_id}/dispensing/{invalid_dispensing_id}",
            404,  # Not found status code
            data=valid_data
        )
        
        # Test 4: Invalid dispensing ID for delete
        success, response = self.run_test(
            "Dispensing - Invalid Dispensing ID for Delete",
            "DELETE",
            f"api/admin-registration/{self.registration_id}/dispensing/{invalid_dispensing_id}",
            404  # Not found status code
        )
        
        return True, {"message": "Dispensing validation tests completed"}

    def test_default_values(self):
        """Test default values for dispensing records"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        print("\n🔍 Testing Dispensing Default Values...")
        
        # Test with minimal data (only required field: medication)
        minimal_data = {
            "medication": "Ecplusa"
        }
        
        success, dispensing_id = self.test_create_dispensing(minimal_data)
        
        if success:
            # Verify default values by getting the record
            get_success, get_response = self.run_test(
                "Verify Dispensing Default Values",
                "GET",
                f"api/admin-registration/{self.registration_id}/dispensing",
                200
            )
            
            if get_success and 'dispensing' in get_response:
                created_record = next((r for r in get_response['dispensing'] if r['id'] == dispensing_id), None)
                if created_record:
                    # Check default values
                    if created_record.get('quantity') == "28":
                        print("✅ Default quantity value '28' was correctly applied")
                    else:
                        print(f"❌ Default quantity value incorrect: expected '28', got '{created_record.get('quantity')}'")
                    
                    if created_record.get('product_type') == "Commercial":
                        print("✅ Default product_type value 'Commercial' was correctly applied")
                    else:
                        print(f"❌ Default product_type value incorrect: expected 'Commercial', got '{created_record.get('product_type')}'")
                else:
                    print("❌ Could not find the created record with default values")
            
            return True, {"message": "Default values test completed"}
        else:
            print("❌ Failed to create dispensing record with minimal data")
            return False, {}

    def test_medication_options(self):
        """Test all medication options for dispensing records"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        print("\n🔍 Testing Dispensing Medication Options...")
        
        # Test all medication options
        medication_options = ["Ecplusa", "Maviret", "Vosevi"]
        
        for medication in medication_options:
            data = {
                "medication": medication,
                "rx": f"RX-{medication}",
                "quantity": "28",
                "lot": f"LOT-{medication}",
                "product_type": "Commercial",
                "expiry_date": "2025-12-31"
            }
            
            success, dispensing_id = self.test_create_dispensing(data)
            
            if success:
                print(f"✅ Successfully created dispensing record with medication: {medication}")
            else:
                print(f"❌ Failed to create dispensing record with medication: {medication}")
        
        return True, {"message": "Medication options test completed"}

    def test_product_type_options(self):
        """Test all product_type options for dispensing records"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        print("\n🔍 Testing Dispensing Product Type Options...")
        
        # Test all product_type options
        product_type_options = ["Commercial", "Compassionate"]
        
        for product_type in product_type_options:
            data = {
                "medication": "Ecplusa",
                "rx": f"RX-{product_type}",
                "quantity": "28",
                "lot": f"LOT-{product_type}",
                "product_type": product_type,
                "expiry_date": "2025-12-31"
            }
            
            success, dispensing_id = self.test_create_dispensing(data)
            
            if success:
                print(f"✅ Successfully created dispensing record with product_type: {product_type}")
            else:
                print(f"❌ Failed to create dispensing record with product_type: {product_type}")
        
        return True, {"message": "Product type options test completed"}

    def test_complete_workflow(self):
        """Test the complete dispensing workflow"""
        print("\n" + "=" * 50)
        print("🔍 Testing Complete Dispensing Workflow")
        print("=" * 50)
        
        # 1. Create a new admin registration
        if not self.create_test_registration():
            return False, {}
        
        # 2. Add multiple dispensing records
        dispensing_data = [
            {
                "medication": "Ecplusa",
                "rx": "RX-001",
                "quantity": "28",
                "lot": "LOT-001",
                "product_type": "Commercial",
                "expiry_date": "2025-12-31"
            },
            {
                "medication": "Maviret",
                "rx": "RX-002",
                "quantity": "56",
                "lot": "LOT-002",
                "product_type": "Compassionate",
                "expiry_date": "2026-06-30"
            },
            {
                "medication": "Vosevi",
                "rx": "RX-003",
                "quantity": "84",
                "lot": "LOT-003",
                "product_type": "Commercial",
                "expiry_date": "2027-01-15"
            }
        ]
        
        for i, data in enumerate(dispensing_data):
            success, dispensing_id = self.test_create_dispensing(data)
            if not success:
                print(f"❌ Failed to create dispensing record #{i+1}")
                return False, {}
        
        # 3. Get all dispensing records and verify count
        get_success, get_response = self.test_get_dispensing()
        if not get_success:
            return False, {}
        
        dispensing_records = get_response
        if len(dispensing_records) != len(dispensing_data):
            print(f"❌ Expected {len(dispensing_data)} dispensing records, got {len(dispensing_records)}")
            return False, {}
        
        print(f"✅ Successfully created and retrieved {len(dispensing_records)} dispensing records")
        
        # 4. Update a dispensing record
        if self.dispensing_ids:
            # Use the most recently created dispensing ID for the update
            dispensing_id = self.dispensing_ids[-1]
            
            update_data = {
                "medication": "Maviret",
                "rx": "RX-UPDATED",
                "quantity": "56",
                "lot": "LOT-UPDATED",
                "product_type": "Compassionate",
                "expiry_date": "2026-06-30"
            }
            
            update_success, update_response = self.run_test(
                "Update Dispensing Record",
                "PUT",
                f"api/admin-registration/{self.registration_id}/dispensing/{dispensing_id}",
                200,
                data=update_data
            )
            
            if update_success:
                print(f"✅ Updated dispensing record with ID: {dispensing_id}")
                
                # Verify the update by getting the record
                get_success, get_response = self.run_test(
                    "Verify Dispensing Update",
                    "GET",
                    f"api/admin-registration/{self.registration_id}/dispensing",
                    200
                )
                
                if get_success and 'dispensing' in get_response:
                    updated_record = next((r for r in get_response['dispensing'] if r['id'] == dispensing_id), None)
                    if updated_record:
                        all_fields_updated = all(
                            updated_record[key] == update_data[key]
                            for key in update_data
                        )
                        if all_fields_updated:
                            print("✅ All fields were correctly updated")
                        else:
                            print("❌ Not all fields were correctly updated")
                            for key in update_data:
                                if key in updated_record and updated_record[key] != update_data[key]:
                                    print(f"  - Field '{key}': expected '{update_data[key]}', got '{updated_record[key]}'")
                    else:
                        print("❌ Could not find the updated record")
            else:
                print("❌ Failed to update dispensing record")
                return False, {}
        
        # 5. Delete a dispensing record
        if self.dispensing_ids:
            # Use the most recently created dispensing ID for the delete
            dispensing_id = self.dispensing_ids[-1]
            
            delete_success, delete_response = self.run_test(
                "Delete Dispensing Record",
                "DELETE",
                f"api/admin-registration/{self.registration_id}/dispensing/{dispensing_id}",
                200
            )
            
            if delete_success:
                print(f"✅ Deleted dispensing record with ID: {dispensing_id}")
                
                # Remove the ID from our list
                if dispensing_id in self.dispensing_ids:
                    self.dispensing_ids.remove(dispensing_id)
                
                # Verify the deletion by getting all records
                final_get_success, final_get_response = self.run_test(
                    "Verify Dispensing Deletion",
                    "GET",
                    f"api/admin-registration/{self.registration_id}/dispensing",
                    200
                )
                
                if final_get_success and 'dispensing' in final_get_response:
                    final_dispensing_records = final_get_response['dispensing']
                    deleted_record = next((r for r in final_dispensing_records if r['id'] == dispensing_id), None)
                    if deleted_record:
                        print("❌ Record was not actually deleted")
                        return False, {}
                    else:
                        print("✅ Record was successfully deleted")
                        
                    expected_count = len(dispensing_data) - 1  # We deleted one record
                    if len(final_dispensing_records) != expected_count:
                        print(f"❌ Expected {expected_count} dispensing records after deletion, got {len(final_dispensing_records)}")
                        return False, {}
                    
                    print(f"✅ Successfully verified {len(final_dispensing_records)} dispensing records after deletion")
            else:
                print("❌ Failed to delete dispensing record")
                return False, {}
        
        return True, {"message": "Complete dispensing workflow test completed successfully"}

    def run_all_tests(self):
        """Run all dispensing API tests"""
        print("🚀 Starting Dispensing API Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Basic CRUD tests
        self.test_create_dispensing()
        self.test_get_dispensing()
        self.test_update_dispensing()
        self.test_delete_dispensing()
        
        # Validation tests
        self.test_dispensing_validation()
        
        # Default values test
        self.test_default_values()
        
        # Options tests
        self.test_medication_options()
        self.test_product_type_options()
        
        # Complete workflow test
        self.test_complete_workflow()
        
        print("\n" + "=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = DispensingAPITester(BACKEND_URL)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())