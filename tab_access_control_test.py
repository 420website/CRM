#!/usr/bin/env python3

"""
Tab Access Control Functionality Backend Testing
==============================================

This script tests the tab access control functionality that was just implemented.
It verifies:
1. Backend User Model - user permissions field works correctly
2. User Creation with Permissions - creating users with specific tab permissions
3. User Login and Session Data - login includes correct permissions
4. Permission Validation - permissions are stored and retrieved properly

Test Scenarios:
1. Create a new user with permissions for only "Client" and "Tests" tabs
2. Verify the user is saved with correct permissions in the database
3. Test user authentication and verify returned session data includes permissions
4. Test creating a user with no permissions and verify empty permissions object
5. Test updating user permissions
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com/api"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_backend_health():
    """Test if backend is accessible"""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if response.status_code == 200:
            log_test("✅ Backend health check passed")
            return True
        else:
            log_test(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        log_test(f"❌ Backend health check failed: {str(e)}")
        return False

def test_user_creation_with_permissions():
    """Test creating a user with specific tab permissions"""
    log_test("🧪 Testing user creation with tab permissions...")
    
    # Test data - user with only Client and Tests tab permissions
    user_data = {
        "firstName": "TestUser",
        "lastName": "TabAccess",
        "email": "testuser.tabaccess@testdomain.com",
        "phone": "4161234567",
        "pin": "1234567890",
        "permissions": {
            "Client": True,
            "Tests": True,
            "Medication": False,
            "Dispensing": False,
            "Notes": False,
            "Activities": False,
            "Interactions": False,
            "Attachments": False
        }
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/users", json=user_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            log_test("✅ User created successfully with tab permissions")
            
            # Verify permissions in response
            returned_permissions = result.get("user", {}).get("permissions", {})
            if returned_permissions.get("Client") == True and returned_permissions.get("Tests") == True:
                log_test("✅ Permissions correctly returned in creation response")
                return result.get("user", {}).get("id")
            else:
                log_test(f"❌ Permissions not correctly returned: {returned_permissions}")
                return None
        elif response.status_code == 400 and "PIN already exists" in response.text:
            log_test("⚠️  PIN already exists, trying different PIN...")
            # Try with different PIN
            user_data["pin"] = "9876543210"
            response = requests.post(f"{BACKEND_URL}/users", json=user_data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                log_test("✅ User created successfully with alternative PIN")
                returned_permissions = result.get("user", {}).get("permissions", {})
                if returned_permissions.get("Client") == True and returned_permissions.get("Tests") == True:
                    log_test("✅ Permissions correctly returned in creation response")
                    return result.get("user", {}).get("id")
            else:
                log_test(f"❌ User creation failed with alternative PIN: {response.status_code}")
                return None
        else:
            log_test(f"❌ User creation failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        log_test(f"❌ User creation test failed: {str(e)}")
        return None

def test_user_retrieval_with_permissions(user_id):
    """Test retrieving user and verifying permissions are stored correctly"""
    log_test("🧪 Testing user retrieval with permissions...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/users/{user_id}", timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            permissions = user_data.get("permissions", {})
            
            # Verify specific permissions
            if (permissions.get("Client") == True and 
                permissions.get("Tests") == True and
                permissions.get("Medication") == False and
                permissions.get("Dispensing") == False):
                log_test("✅ User permissions correctly stored and retrieved")
                log_test(f"   Client: {permissions.get('Client')}")
                log_test(f"   Tests: {permissions.get('Tests')}")
                log_test(f"   Medication: {permissions.get('Medication')}")
                log_test(f"   Dispensing: {permissions.get('Dispensing')}")
                return True
            else:
                log_test(f"❌ Permissions not correctly stored: {permissions}")
                return False
        else:
            log_test(f"❌ User retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        log_test(f"❌ User retrieval test failed: {str(e)}")
        return False

def test_user_authentication_with_permissions():
    """Test user authentication and verify permissions are included in session data"""
    log_test("🧪 Testing user authentication with permissions...")
    
    try:
        # Test PIN verification which should return permissions
        response = requests.post(f"{BACKEND_URL}/auth/pin-verify", json={"pin": "9876543210"}, timeout=30)
        
        if response.status_code == 200:
            auth_data = response.json()
            permissions = auth_data.get("permissions", {})
            
            # Verify permissions are included in authentication response
            if (auth_data.get("pin_valid") == True and 
                permissions.get("Client") == True and
                permissions.get("Tests") == True):
                log_test("✅ User authentication includes correct permissions")
                log_test(f"   User Type: {auth_data.get('user_type')}")
                log_test(f"   Session Token: {'Present' if auth_data.get('session_token') else 'Missing'}")
                log_test(f"   Permissions: Client={permissions.get('Client')}, Tests={permissions.get('Tests')}")
                return True
            else:
                log_test(f"❌ Authentication response missing or incorrect permissions: {permissions}")
                return False
        else:
            log_test(f"❌ User authentication failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        log_test(f"❌ User authentication test failed: {str(e)}")
        return False

def test_user_creation_with_no_permissions():
    """Test creating a user with no permissions (empty permissions object)"""
    log_test("🧪 Testing user creation with no permissions...")
    
    user_data = {
        "firstName": "TestUser",
        "lastName": "NoPermissions",
        "email": "testuser.nopermissions@testdomain.com",
        "phone": "4169876543",
        "pin": "0987654321",
        "permissions": {}  # Empty permissions
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/users", json=user_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            returned_permissions = result.get("user", {}).get("permissions", {})
            
            if isinstance(returned_permissions, dict) and len(returned_permissions) == 0:
                log_test("✅ User created successfully with empty permissions object")
                return result.get("user", {}).get("id")
            else:
                log_test(f"❌ Permissions not correctly handled: {returned_permissions}")
                return None
        else:
            log_test(f"❌ User creation with no permissions failed: {response.status_code}")
            return None
            
    except Exception as e:
        log_test(f"❌ User creation with no permissions test failed: {str(e)}")
        return None

def test_user_permission_update(user_id):
    """Test updating user permissions"""
    log_test("🧪 Testing user permission updates...")
    
    # Update permissions to add more tabs
    update_data = {
        "permissions": {
            "Client": True,
            "Tests": True,
            "Medication": True,  # Add medication access
            "Dispensing": False,
            "Notes": True,       # Add notes access
            "Activities": False,
            "Interactions": False,
            "Attachments": False
        }
    }
    
    try:
        response = requests.put(f"{BACKEND_URL}/users/{user_id}", json=update_data, timeout=10)
        
        if response.status_code == 200:
            # Verify the update by retrieving the user
            get_response = requests.get(f"{BACKEND_URL}/users/{user_id}", timeout=10)
            
            if get_response.status_code == 200:
                user_data = get_response.json()
                permissions = user_data.get("permissions", {})
                
                if (permissions.get("Client") == True and 
                    permissions.get("Tests") == True and
                    permissions.get("Medication") == True and
                    permissions.get("Notes") == True):
                    log_test("✅ User permissions updated successfully")
                    log_test(f"   Updated permissions: Medication={permissions.get('Medication')}, Notes={permissions.get('Notes')}")
                    return True
                else:
                    log_test(f"❌ Permissions not correctly updated: {permissions}")
                    return False
            else:
                log_test(f"❌ Failed to retrieve updated user: {get_response.status_code}")
                return False
        else:
            log_test(f"❌ User permission update failed: {response.status_code}")
            return False
            
    except Exception as e:
        log_test(f"❌ User permission update test failed: {str(e)}")
        return False

def test_permission_validation():
    """Test that permissions are properly validated and stored"""
    log_test("🧪 Testing permission validation...")
    
    # Test with various permission structures
    test_cases = [
        {
            "name": "All tabs enabled",
            "permissions": {
                "Client": True,
                "Tests": True,
                "Medication": True,
                "Dispensing": True,
                "Notes": True,
                "Activities": True,
                "Interactions": True,
                "Attachments": True
            }
        },
        {
            "name": "Mixed permissions",
            "permissions": {
                "Client": True,
                "Tests": False,
                "Medication": True,
                "Dispensing": False,
                "Notes": True,
                "Activities": False,
                "Interactions": True,
                "Attachments": False
            }
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases):
        user_data = {
            "firstName": "TestUser",
            "lastName": f"Validation{i}",
            "email": f"testuser.validation{i}@testdomain.com",
            "phone": f"416555000{i}",
            "pin": f"111111111{i}",
            "permissions": test_case["permissions"]
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/users", json=user_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                returned_permissions = result.get("user", {}).get("permissions", {})
                
                # Verify all permissions match
                if returned_permissions == test_case["permissions"]:
                    log_test(f"✅ {test_case['name']} - permissions validated correctly")
                    success_count += 1
                else:
                    log_test(f"❌ {test_case['name']} - permissions mismatch")
            else:
                log_test(f"❌ {test_case['name']} - creation failed: {response.status_code}")
                
        except Exception as e:
            log_test(f"❌ {test_case['name']} - test failed: {str(e)}")
    
    return success_count == len(test_cases)

def cleanup_test_users():
    """Clean up test users created during testing"""
    log_test("🧹 Cleaning up test users...")
    
    try:
        # Get all users
        response = requests.get(f"{BACKEND_URL}/users", timeout=10)
        
        if response.status_code == 200:
            users = response.json()
            deleted_count = 0
            
            for user in users:
                # Delete test users (those with test emails)
                if "testdomain.com" in user.get("email", ""):
                    delete_response = requests.delete(f"{BACKEND_URL}/users/{user['id']}", timeout=10)
                    if delete_response.status_code == 200:
                        deleted_count += 1
            
            log_test(f"✅ Cleaned up {deleted_count} test users")
            return True
        else:
            log_test(f"❌ Failed to get users for cleanup: {response.status_code}")
            return False
            
    except Exception as e:
        log_test(f"❌ Cleanup failed: {str(e)}")
        return False

def main():
    """Main test execution"""
    log_test("🚀 Starting Tab Access Control Functionality Backend Testing")
    log_test("=" * 70)
    
    # Test results tracking
    tests_passed = 0
    total_tests = 6
    
    # 1. Backend Health Check
    if test_backend_health():
        tests_passed += 1
    
    # 2. User Creation with Permissions
    user_id = test_user_creation_with_permissions()
    if user_id:
        tests_passed += 1
        
        # 3. User Retrieval with Permissions
        if test_user_retrieval_with_permissions(user_id):
            tests_passed += 1
        
        # 4. User Authentication with Permissions
        if test_user_authentication_with_permissions():
            tests_passed += 1
        
        # 5. User Permission Update
        if test_user_permission_update(user_id):
            tests_passed += 1
    
    # 6. User Creation with No Permissions
    no_perm_user_id = test_user_creation_with_no_permissions()
    if no_perm_user_id:
        tests_passed += 1
    
    # 7. Permission Validation (bonus test)
    if test_permission_validation():
        log_test("✅ Bonus: Permission validation test passed")
    
    # Cleanup
    cleanup_test_users()
    
    # Results Summary
    log_test("=" * 70)
    log_test("🎯 TAB ACCESS CONTROL TESTING RESULTS:")
    log_test(f"   Tests Passed: {tests_passed}/{total_tests}")
    log_test(f"   Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        log_test("🎉 ALL TESTS PASSED - Tab access control functionality is working correctly!")
        log_test("✅ Backend User Model: User permissions field works correctly")
        log_test("✅ User Creation with Permissions: Creating users with specific tab permissions works")
        log_test("✅ User Login and Session Data: Login includes correct permissions")
        log_test("✅ Permission Validation: Permissions are stored and retrieved properly")
    else:
        log_test("⚠️  Some tests failed - see details above")
    
    log_test("=" * 70)
    return tests_passed == total_tests

if __name__ == "__main__":
    main()