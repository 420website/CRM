import requests
import unittest
import json
from datetime import datetime, date
import random
import string
import sys
import os
from dotenv import load_dotenv

class InteractionsAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {}
        self.registration_id = None
        self.interaction_id = None

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
        today = date.today()
        
        self.test_data = {
            "admin_registration": {
                "firstName": f"Michael {random_suffix}",
                "lastName": f"Smith {random_suffix}",
                "patientConsent": "Verbal",
                "gender": "Male",
                "province": "Ontario"
            },
            "interaction": {
                "date": today.isoformat(),
                "description": "Screening",
                "amount": "25.00",
                "location": "Toronto",
                "issued": "Yes"
            },
            "interaction_update": {
                "date": today.isoformat(),
                "description": "Adherence",
                "amount": "30.00",
                "location": "Ottawa",
                "issued": "No"
            },
            "interaction_required_only": {
                "description": "Bloodwork"
            }
        }
        
        return self.test_data

    def test_api_health(self):
        """Test the API health endpoint"""
        return self.run_test(
            "API Health Check",
            "GET",
            "api",
            200
        )

    def create_admin_registration(self):
        """Create a new admin registration for testing interactions"""
        if not self.test_data:
            self.generate_test_data()
            
        success, response = self.run_test(
            "Create Admin Registration",
            "POST",
            "api/admin-register",
            200,
            data=self.test_data["admin_registration"]
        )
        
        if success:
            print(f"Admin Registration ID: {response.get('registration_id')}")
            self.registration_id = response.get('registration_id')
            
        return success, response

    def test_create_interaction(self):
        """Test creating a new interaction with all fields"""
        if not self.registration_id:
            success, _ = self.create_admin_registration()
            if not success:
                print("❌ Failed to create admin registration for interaction test")
                return False, {}
        
        success, response = self.run_test(
            "Create Interaction - All Fields",
            "POST",
            f"api/admin-registration/{self.registration_id}/interaction",
            200,
            data=self.test_data["interaction"]
        )
        
        if success:
            print(f"Interaction ID: {response.get('interaction_id')}")
            self.interaction_id = response.get('interaction_id')
            
        return success, response

    def test_create_interaction_required_only(self):
        """Test creating a new interaction with only required fields"""
        if not self.registration_id:
            success, _ = self.create_admin_registration()
            if not success:
                print("❌ Failed to create admin registration for interaction test")
                return False, {}
        
        success, response = self.run_test(
            "Create Interaction - Required Fields Only",
            "POST",
            f"api/admin-registration/{self.registration_id}/interaction",
            200,
            data=self.test_data["interaction_required_only"]
        )
        
        if success:
            print(f"Interaction ID (required fields only): {response.get('interaction_id')}")
            
        return success, response

    def test_get_interactions(self):
        """Test getting all interactions for a registration"""
        if not self.registration_id:
            success, _ = self.create_admin_registration()
            if not success:
                print("❌ Failed to create admin registration for interaction test")
                return False, {}
                
        if not self.interaction_id:
            success, _ = self.test_create_interaction()
            if not success:
                print("❌ Failed to create interaction for test")
                return False, {}
        
        success, response = self.run_test(
            "Get Interactions",
            "GET",
            f"api/admin-registration/{self.registration_id}/interactions",
            200
        )
        
        if success:
            interactions = response.get('interactions', [])
            print(f"Found {len(interactions)} interactions")
            
            # Verify the interaction we created is in the list
            found = False
            for interaction in interactions:
                if interaction.get('id') == self.interaction_id:
                    found = True
                    print("✅ Found our created interaction in the list")
                    
                    # Verify all fields were saved correctly
                    for key, value in self.test_data["interaction"].items():
                        if key in interaction and str(interaction[key]) == str(value):
                            print(f"✅ Field '{key}' saved correctly: {value}")
                        elif key in interaction:
                            print(f"❌ Field '{key}' value mismatch: expected '{value}', got '{interaction[key]}'")
                        else:
                            print(f"❌ Field '{key}' missing from saved interaction")
                    
                    break
            
            if not found:
                print("❌ Could not find our created interaction in the list")
                return False, response
            
        return success, response

    def test_update_interaction(self):
        """Test updating an existing interaction"""
        if not self.registration_id:
            success, _ = self.create_admin_registration()
            if not success:
                print("❌ Failed to create admin registration for interaction test")
                return False, {}
                
        if not self.interaction_id:
            success, _ = self.test_create_interaction()
            if not success:
                print("❌ Failed to create interaction for test")
                return False, {}
        
        success, response = self.run_test(
            "Update Interaction",
            "PUT",
            f"api/admin-registration/{self.registration_id}/interaction/{self.interaction_id}",
            200,
            data=self.test_data["interaction_update"]
        )
        
        if success:
            print(f"Interaction updated successfully: {response.get('message')}")
            
            # Verify the update by getting the interaction again
            get_success, get_response = self.run_test(
                "Get Interactions After Update",
                "GET",
                f"api/admin-registration/{self.registration_id}/interactions",
                200
            )
            
            if get_success:
                interactions = get_response.get('interactions', [])
                found = False
                for interaction in interactions:
                    if interaction.get('id') == self.interaction_id:
                        found = True
                        print("✅ Found our updated interaction in the list")
                        
                        # Verify all fields were updated correctly
                        for key, value in self.test_data["interaction_update"].items():
                            if key in interaction and str(interaction[key]) == str(value):
                                print(f"✅ Field '{key}' updated correctly: {value}")
                            elif key in interaction:
                                print(f"❌ Field '{key}' update failed: expected '{value}', got '{interaction[key]}'")
                            else:
                                print(f"❌ Field '{key}' missing from updated interaction")
                        
                        break
                
                if not found:
                    print("❌ Could not find our updated interaction in the list")
                    return False, get_response
            
        return success, response

    def test_delete_interaction(self):
        """Test deleting an interaction"""
        if not self.registration_id:
            success, _ = self.create_admin_registration()
            if not success:
                print("❌ Failed to create admin registration for interaction test")
                return False, {}
                
        if not self.interaction_id:
            success, _ = self.test_create_interaction()
            if not success:
                print("❌ Failed to create interaction for test")
                return False, {}
        
        success, response = self.run_test(
            "Delete Interaction",
            "DELETE",
            f"api/admin-registration/{self.registration_id}/interaction/{self.interaction_id}",
            200
        )
        
        if success:
            print(f"Interaction deleted successfully: {response.get('message')}")
            
            # Verify the deletion by getting the interactions again
            get_success, get_response = self.run_test(
                "Get Interactions After Deletion",
                "GET",
                f"api/admin-registration/{self.registration_id}/interactions",
                200
            )
            
            if get_success:
                interactions = get_response.get('interactions', [])
                for interaction in interactions:
                    if interaction.get('id') == self.interaction_id:
                        print("❌ Interaction was not deleted - still found in the list")
                        return False, get_response
                
                print("✅ Interaction was successfully deleted - not found in the list")
            
        return success, response

    def test_create_interaction_invalid_registration(self):
        """Test creating an interaction with an invalid registration ID"""
        invalid_id = "invalid_registration_id"
        
        success, response = self.run_test(
            "Create Interaction - Invalid Registration ID",
            "POST",
            f"api/admin-registration/{invalid_id}/interaction",
            404,  # Expecting 404 Not Found
            data=self.test_data["interaction"]
        )
        
        return success, response

    def test_create_interaction_missing_required(self):
        """Test creating an interaction with missing required fields"""
        if not self.registration_id:
            success, _ = self.create_admin_registration()
            if not success:
                print("❌ Failed to create admin registration for interaction test")
                return False, {}
        
        # Create data with missing description (required field)
        invalid_data = {
            "date": self.test_data["interaction"]["date"],
            "amount": self.test_data["interaction"]["amount"],
            "location": self.test_data["interaction"]["location"],
            "issued": self.test_data["interaction"]["issued"]
        }
        
        success, response = self.run_test(
            "Create Interaction - Missing Required Fields",
            "POST",
            f"api/admin-registration/{self.registration_id}/interaction",
            422,  # Expecting 422 Unprocessable Entity
            data=invalid_data
        )
        
        return success, response

    def test_update_interaction_nonexistent(self):
        """Test updating a non-existent interaction"""
        if not self.registration_id:
            success, _ = self.create_admin_registration()
            if not success:
                print("❌ Failed to create admin registration for interaction test")
                return False, {}
        
        nonexistent_id = "nonexistent_interaction_id"
        
        success, response = self.run_test(
            "Update Interaction - Non-existent ID",
            "PUT",
            f"api/admin-registration/{self.registration_id}/interaction/{nonexistent_id}",
            404,  # Expecting 404 Not Found
            data=self.test_data["interaction_update"]
        )
        
        return success, response

    def test_delete_interaction_nonexistent(self):
        """Test deleting a non-existent interaction"""
        if not self.registration_id:
            success, _ = self.create_admin_registration()
            if not success:
                print("❌ Failed to create admin registration for interaction test")
                return False, {}
        
        nonexistent_id = "nonexistent_interaction_id"
        
        success, response = self.run_test(
            "Delete Interaction - Non-existent ID",
            "DELETE",
            f"api/admin-registration/{self.registration_id}/interaction/{nonexistent_id}",
            404  # Expecting 404 Not Found
        )
        
        return success, response

    def test_interaction_description_options(self):
        """Test creating interactions with different description options"""
        if not self.registration_id:
            success, _ = self.create_admin_registration()
            if not success:
                print("❌ Failed to create admin registration for interaction test")
                return False, {}
        
        description_options = [
            "Screening", "Adherence", "Bloodwork", "Discretionary", "Referral", 
            "Consultation", "Outreach", "Repeat", "Results", "Safe Supply", 
            "Lab Req", "Telephone", "Remittance", "Update", "Counselling", 
            "Trillium", "Housing", "SOT", "EOT", "SVR", "Locate", "Staff"
        ]
        
        all_passed = True
        for description in description_options:
            test_data = {
                "description": description,
                "date": self.test_data["interaction"]["date"]
            }
            
            success, response = self.run_test(
                f"Create Interaction - Description: {description}",
                "POST",
                f"api/admin-registration/{self.registration_id}/interaction",
                200,
                data=test_data
            )
            
            if not success:
                all_passed = False
        
        return all_passed, {"message": "Description options tests completed"}

    def test_interaction_issued_options(self):
        """Test creating interactions with different issued options"""
        if not self.registration_id:
            success, _ = self.create_admin_registration()
            if not success:
                print("❌ Failed to create admin registration for interaction test")
                return False, {}
        
        issued_options = ["Yes", "No", "Select"]
        
        all_passed = True
        for issued in issued_options:
            test_data = {
                "description": "Screening",
                "issued": issued
            }
            
            success, response = self.run_test(
                f"Create Interaction - Issued: {issued}",
                "POST",
                f"api/admin-registration/{self.registration_id}/interaction",
                200,
                data=test_data
            )
            
            if not success:
                all_passed = False
        
        return all_passed, {"message": "Issued options tests completed"}

    def test_interaction_sorting(self):
        """Test that interactions are returned in the correct order (newest first)"""
        if not self.registration_id:
            success, _ = self.create_admin_registration()
            if not success:
                print("❌ Failed to create admin registration for interaction test")
                return False, {}
        
        # Create multiple interactions
        for i in range(3):
            test_data = {
                "description": f"Test {i+1}",
                "date": date.today().isoformat()
            }
            
            success, response = self.run_test(
                f"Create Interaction {i+1} for Sorting Test",
                "POST",
                f"api/admin-registration/{self.registration_id}/interaction",
                200,
                data=test_data
            )
            
            if not success:
                print(f"❌ Failed to create interaction {i+1} for sorting test")
                return False, {}
        
        # Get all interactions and check order
        success, response = self.run_test(
            "Get Interactions for Sorting Test",
            "GET",
            f"api/admin-registration/{self.registration_id}/interactions",
            200
        )
        
        if success:
            interactions = response.get('interactions', [])
            if len(interactions) < 3:
                print(f"❌ Expected at least 3 interactions, but found {len(interactions)}")
                return False, response
            
            # Check if sorted by created_at (newest first)
            is_sorted = True
            for i in range(len(interactions) - 1):
                current_time = datetime.fromisoformat(interactions[i]['created_at'].replace('Z', '+00:00'))
                next_time = datetime.fromisoformat(interactions[i+1]['created_at'].replace('Z', '+00:00'))
                
                if current_time < next_time:
                    is_sorted = False
                    print(f"❌ Interactions not sorted correctly: {current_time} should be after {next_time}")
                    break
            
            if is_sorted:
                print("✅ Interactions are correctly sorted by created_at (newest first)")
            else:
                return False, response
        
        return success, response

    def run_all_tests(self):
        """Run all Interactions API tests"""
        print("🚀 Starting Interactions API Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        self.test_api_health()
        
        # Generate test data
        self.generate_test_data()
        
        # Create a registration for testing
        self.create_admin_registration()
        
        # Basic CRUD operations
        self.test_create_interaction()
        self.test_create_interaction_required_only()
        self.test_get_interactions()
        self.test_update_interaction()
        
        # Test options
        self.test_interaction_description_options()
        self.test_interaction_issued_options()
        
        # Test sorting
        self.test_interaction_sorting()
        
        # Error handling
        self.test_create_interaction_invalid_registration()
        self.test_create_interaction_missing_required()
        self.test_update_interaction_nonexistent()
        self.test_delete_interaction_nonexistent()
        
        # Delete test (do this last since it removes the interaction)
        self.test_delete_interaction()
        
        print("\n" + "=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run


def main():
    # Get the backend URL from the frontend .env file
    import os
    from dotenv import load_dotenv
    
    # Load the frontend .env file
    load_dotenv('/app/frontend/.env')
    
    # Get the backend URL from the environment variable
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return 1
    
    print(f"🔗 Using backend URL from .env: {backend_url}")
    
    # Run the tests
    tester = InteractionsAPITester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())