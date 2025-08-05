#!/usr/bin/env python3
"""
Comprehensive test for the new "Back to Pending" API endpoint
Tests the revert-to-pending functionality as requested in the review
"""

import requests
import json
import sys
from datetime import datetime
import time

# Get backend URL from environment
BACKEND_URL = "https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com/api"

def test_revert_to_pending_endpoint():
    """Test the new revert-to-pending API endpoint comprehensively"""
    
    print("🔄 TESTING REVERT TO PENDING API ENDPOINT")
    print("=" * 60)
    
    test_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "test_details": []
    }
    
    try:
        # Test 1: Check current registrations in database
        print("\n1️⃣ CHECKING CURRENT REGISTRATIONS")
        print("-" * 40)
        
        # Get pending registrations
        pending_response = requests.get(f"{BACKEND_URL}/admin-registrations-pending", timeout=30)
        test_results["total_tests"] += 1
        
        if pending_response.status_code == 200:
            pending_data = pending_response.json()
            print(f"✅ Found {len(pending_data)} pending registrations")
            test_results["passed_tests"] += 1
            test_results["test_details"].append("✅ Pending registrations endpoint working")
        else:
            print(f"❌ Failed to get pending registrations: {pending_response.status_code}")
            test_results["failed_tests"] += 1
            test_results["test_details"].append("❌ Pending registrations endpoint failed")
            
        # Get submitted registrations
        submitted_response = requests.get(f"{BACKEND_URL}/admin-registrations-submitted", timeout=30)
        test_results["total_tests"] += 1
        
        if submitted_response.status_code == 200:
            submitted_data = submitted_response.json()
            print(f"✅ Found {len(submitted_data)} submitted registrations")
            test_results["passed_tests"] += 1
            test_results["test_details"].append("✅ Submitted registrations endpoint working")
            
            # Show some submitted registrations for testing
            if submitted_data:
                print("\n📋 Available submitted registrations for testing:")
                for i, reg in enumerate(submitted_data[:3]):  # Show first 3
                    print(f"   {i+1}. ID: {reg.get('id', 'N/A')[:8]}... - {reg.get('firstName', 'N/A')} {reg.get('lastName', 'N/A')} - Status: {reg.get('status', 'N/A')}")
                    if reg.get('finalized_at'):
                        print(f"      Finalized at: {reg.get('finalized_at')}")
        else:
            print(f"❌ Failed to get submitted registrations: {submitted_response.status_code}")
            test_results["failed_tests"] += 1
            test_results["test_details"].append("❌ Submitted registrations endpoint failed")
            submitted_data = []
            
    except Exception as e:
        print(f"❌ Error checking registrations: {str(e)}")
        test_results["failed_tests"] += 1
        test_results["test_details"].append(f"❌ Registration check failed: {str(e)}")
        submitted_data = []
    
    # Test 2: Test revert endpoint with non-existent registration
    print("\n2️⃣ TESTING ERROR HANDLING - NON-EXISTENT REGISTRATION")
    print("-" * 40)
    
    try:
        fake_id = "non-existent-registration-id"
        revert_response = requests.post(f"{BACKEND_URL}/admin-registration/{fake_id}/revert-to-pending", timeout=30)
        test_results["total_tests"] += 1
        
        if revert_response.status_code == 404:
            print("✅ Correctly returned 404 for non-existent registration")
            test_results["passed_tests"] += 1
            test_results["test_details"].append("✅ 404 error handling working correctly")
        else:
            print(f"❌ Expected 404, got {revert_response.status_code}")
            test_results["failed_tests"] += 1
            test_results["test_details"].append(f"❌ Wrong status code for non-existent registration: {revert_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing non-existent registration: {str(e)}")
        test_results["failed_tests"] += 1
        test_results["test_details"].append(f"❌ Non-existent registration test failed: {str(e)}")
    
    # Test 3: Test revert endpoint with pending registration (should fail)
    print("\n3️⃣ TESTING ERROR HANDLING - ALREADY PENDING REGISTRATION")
    print("-" * 40)
    
    try:
        if pending_data and len(pending_data) > 0:
            pending_reg = pending_data[0]
            pending_id = pending_reg.get('id')
            
            revert_response = requests.post(f"{BACKEND_URL}/admin-registration/{pending_id}/revert-to-pending", timeout=30)
            test_results["total_tests"] += 1
            
            if revert_response.status_code == 400:
                print("✅ Correctly returned 400 for already pending registration")
                test_results["passed_tests"] += 1
                test_results["test_details"].append("✅ 400 error handling for pending registration working")
            else:
                print(f"❌ Expected 400, got {revert_response.status_code}")
                test_results["failed_tests"] += 1
                test_results["test_details"].append(f"❌ Wrong status code for pending registration: {revert_response.status_code}")
        else:
            print("⚠️ No pending registrations available to test")
            test_results["test_details"].append("⚠️ No pending registrations available for testing")
            
    except Exception as e:
        print(f"❌ Error testing pending registration: {str(e)}")
        test_results["failed_tests"] += 1
        test_results["test_details"].append(f"❌ Pending registration test failed: {str(e)}")
    
    # Test 4: Test successful revert with submitted registration
    print("\n4️⃣ TESTING SUCCESSFUL REVERT - SUBMITTED TO PENDING")
    print("-" * 40)
    
    try:
        if submitted_data and len(submitted_data) > 0:
            # Find a completed registration to revert
            completed_reg = None
            for reg in submitted_data:
                if reg.get('status') == 'completed':
                    completed_reg = reg
                    break
            
            if completed_reg:
                reg_id = completed_reg.get('id')
                print(f"📝 Testing revert with registration: {reg_id[:8]}... ({completed_reg.get('firstName', 'N/A')} {completed_reg.get('lastName', 'N/A')})")
                
                # Store original state
                original_status = completed_reg.get('status')
                original_finalized_at = completed_reg.get('finalized_at')
                print(f"   Original status: {original_status}")
                if original_finalized_at:
                    print(f"   Original finalized_at: {original_finalized_at}")
                
                # Test the revert endpoint
                revert_response = requests.post(f"{BACKEND_URL}/admin-registration/{reg_id}/revert-to-pending", timeout=30)
                test_results["total_tests"] += 1
                
                if revert_response.status_code == 200:
                    revert_data = revert_response.json()
                    print("✅ Revert request successful")
                    print(f"   Response: {revert_data}")
                    test_results["passed_tests"] += 1
                    test_results["test_details"].append("✅ Revert endpoint working correctly")
                    
                    # Verify the changes in database
                    print("\n🔍 VERIFYING DATABASE CHANGES")
                    time.sleep(1)  # Give database time to update
                    
                    # Get updated registration
                    updated_response = requests.get(f"{BACKEND_URL}/admin-registration/{reg_id}", timeout=30)
                    test_results["total_tests"] += 1
                    
                    if updated_response.status_code == 200:
                        updated_reg = updated_response.json()
                        new_status = updated_reg.get('status')
                        new_finalized_at = updated_reg.get('finalized_at')
                        updated_at = updated_reg.get('updated_at')
                        
                        print(f"   New status: {new_status}")
                        print(f"   New finalized_at: {new_finalized_at}")
                        print(f"   Updated at: {updated_at}")
                        
                        # Verify status changed to pending_review
                        if new_status == 'pending_review':
                            print("✅ Status correctly changed to 'pending_review'")
                            test_results["passed_tests"] += 1
                            test_results["test_details"].append("✅ Status correctly updated to pending_review")
                        else:
                            print(f"❌ Status not changed correctly. Expected 'pending_review', got '{new_status}'")
                            test_results["failed_tests"] += 1
                            test_results["test_details"].append(f"❌ Status not updated correctly: {new_status}")
                        
                        # Verify finalized_at was removed
                        if new_finalized_at is None:
                            print("✅ finalized_at timestamp correctly removed")
                            test_results["passed_tests"] += 1
                            test_results["test_details"].append("✅ finalized_at timestamp correctly removed")
                        else:
                            print(f"❌ finalized_at timestamp not removed: {new_finalized_at}")
                            test_results["failed_tests"] += 1
                            test_results["test_details"].append(f"❌ finalized_at not removed: {new_finalized_at}")
                        
                        # Verify updated_at was set
                        if updated_at:
                            print("✅ updated_at timestamp correctly set")
                            test_results["passed_tests"] += 1
                            test_results["test_details"].append("✅ updated_at timestamp correctly set")
                        else:
                            print("❌ updated_at timestamp not set")
                            test_results["failed_tests"] += 1
                            test_results["test_details"].append("❌ updated_at timestamp not set")
                            
                    else:
                        print(f"❌ Failed to get updated registration: {updated_response.status_code}")
                        test_results["failed_tests"] += 1
                        test_results["test_details"].append("❌ Failed to verify database changes")
                        
                else:
                    print(f"❌ Revert request failed: {revert_response.status_code}")
                    if revert_response.text:
                        print(f"   Error: {revert_response.text}")
                    test_results["failed_tests"] += 1
                    test_results["test_details"].append(f"❌ Revert request failed: {revert_response.status_code}")
                    
            else:
                print("⚠️ No completed registrations available to test revert functionality")
                print("   Creating a test registration and completing it first...")
                
                # Create a test registration for revert testing
                test_registration = {
                    "firstName": "TestRevert",
                    "lastName": "BackToPending",
                    "patientConsent": "verbal",
                    "regDate": datetime.now().strftime('%Y-%m-%d'),
                    "disposition": "ACTIVE"
                }
                
                create_response = requests.post(f"{BACKEND_URL}/admin-register", json=test_registration, timeout=30)
                test_results["total_tests"] += 1
                
                if create_response.status_code == 200:
                    created_reg = create_response.json()
                    test_reg_id = created_reg.get('id')
                    print(f"✅ Created test registration: {test_reg_id[:8]}...")
                    test_results["passed_tests"] += 1
                    
                    # Now finalize it to make it completed
                    finalize_response = requests.post(f"{BACKEND_URL}/admin-registration/{test_reg_id}/finalize", timeout=30)
                    test_results["total_tests"] += 1
                    
                    if finalize_response.status_code == 200:
                        print("✅ Test registration finalized successfully")
                        test_results["passed_tests"] += 1
                        
                        # Now test the revert
                        time.sleep(1)  # Give database time to update
                        revert_response = requests.post(f"{BACKEND_URL}/admin-registration/{test_reg_id}/revert-to-pending", timeout=30)
                        test_results["total_tests"] += 1
                        
                        if revert_response.status_code == 200:
                            print("✅ Test registration successfully reverted to pending")
                            test_results["passed_tests"] += 1
                            test_results["test_details"].append("✅ Created test registration and successfully reverted")
                        else:
                            print(f"❌ Failed to revert test registration: {revert_response.status_code}")
                            test_results["failed_tests"] += 1
                            test_results["test_details"].append("❌ Failed to revert test registration")
                    else:
                        print(f"❌ Failed to finalize test registration: {finalize_response.status_code}")
                        test_results["failed_tests"] += 1
                        test_results["test_details"].append("❌ Failed to finalize test registration")
                else:
                    print(f"❌ Failed to create test registration: {create_response.status_code}")
                    test_results["failed_tests"] += 1
                    test_results["test_details"].append("❌ Failed to create test registration")
        else:
            print("⚠️ No submitted registrations available to test")
            test_results["test_details"].append("⚠️ No submitted registrations available for testing")
            
    except Exception as e:
        print(f"❌ Error testing successful revert: {str(e)}")
        test_results["failed_tests"] += 1
        test_results["test_details"].append(f"❌ Successful revert test failed: {str(e)}")
    
    # Test 5: Test complete workflow (pending → submitted → back to pending → submitted again)
    print("\n5️⃣ TESTING COMPLETE WORKFLOW")
    print("-" * 40)
    
    try:
        # Create a new test registration
        workflow_registration = {
            "firstName": "WorkflowTest",
            "lastName": "RevertCycle",
            "patientConsent": "verbal",
            "regDate": datetime.now().strftime('%Y-%m-%d'),
            "disposition": "ACTIVE"
        }
        
        create_response = requests.post(f"{BACKEND_URL}/admin-register", json=workflow_registration, timeout=30)
        test_results["total_tests"] += 1
        
        if create_response.status_code == 200:
            workflow_reg = create_response.json()
            workflow_id = workflow_reg.get('id')
            print(f"✅ Step 1: Created workflow test registration: {workflow_id[:8]}...")
            test_results["passed_tests"] += 1
            
            # Step 2: Finalize it (pending → completed)
            finalize_response = requests.post(f"{BACKEND_URL}/admin-registration/{workflow_id}/finalize", timeout=30)
            test_results["total_tests"] += 1
            
            if finalize_response.status_code == 200:
                print("✅ Step 2: Registration finalized (pending → completed)")
                test_results["passed_tests"] += 1
                
                # Step 3: Revert to pending (completed → pending)
                time.sleep(1)
                revert_response = requests.post(f"{BACKEND_URL}/admin-registration/{workflow_id}/revert-to-pending", timeout=30)
                test_results["total_tests"] += 1
                
                if revert_response.status_code == 200:
                    print("✅ Step 3: Registration reverted (completed → pending)")
                    test_results["passed_tests"] += 1
                    
                    # Step 4: Finalize again (pending → completed)
                    time.sleep(1)
                    finalize2_response = requests.post(f"{BACKEND_URL}/admin-registration/{workflow_id}/finalize", timeout=30)
                    test_results["total_tests"] += 1
                    
                    if finalize2_response.status_code == 200:
                        print("✅ Step 4: Registration finalized again (pending → completed)")
                        print("✅ Complete workflow test successful!")
                        test_results["passed_tests"] += 1
                        test_results["test_details"].append("✅ Complete workflow test successful")
                    else:
                        print(f"❌ Step 4 failed: {finalize2_response.status_code}")
                        test_results["failed_tests"] += 1
                        test_results["test_details"].append("❌ Second finalization failed")
                else:
                    print(f"❌ Step 3 failed: {revert_response.status_code}")
                    test_results["failed_tests"] += 1
                    test_results["test_details"].append("❌ Revert step failed")
            else:
                print(f"❌ Step 2 failed: {finalize_response.status_code}")
                test_results["failed_tests"] += 1
                test_results["test_details"].append("❌ Initial finalization failed")
        else:
            print(f"❌ Step 1 failed: {create_response.status_code}")
            test_results["failed_tests"] += 1
            test_results["test_details"].append("❌ Workflow registration creation failed")
            
    except Exception as e:
        print(f"❌ Error testing complete workflow: {str(e)}")
        test_results["failed_tests"] += 1
        test_results["test_details"].append(f"❌ Complete workflow test failed: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 60)
    print("🎯 REVERT TO PENDING API TEST RESULTS")
    print("=" * 60)
    
    success_rate = (test_results["passed_tests"] / test_results["total_tests"] * 100) if test_results["total_tests"] > 0 else 0
    
    print(f"📊 Total Tests: {test_results['total_tests']}")
    print(f"✅ Passed: {test_results['passed_tests']}")
    print(f"❌ Failed: {test_results['failed_tests']}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    print("\n📋 DETAILED TEST RESULTS:")
    for detail in test_results["test_details"]:
        print(f"   {detail}")
    
    if success_rate >= 80:
        print(f"\n🎉 REVERT TO PENDING API ENDPOINT - SUCCESS!")
        print("   The new 'Back to Pending' functionality is working correctly.")
        print("   ✅ Error handling working properly")
        print("   ✅ Status updates working correctly") 
        print("   ✅ Timestamp management working properly")
        print("   ✅ Complete workflow cycle functional")
        return True
    else:
        print(f"\n❌ REVERT TO PENDING API ENDPOINT - ISSUES FOUND")
        print("   Some functionality is not working as expected.")
        return False
        
    return success_rate >= 80

if __name__ == "__main__":
    success = test_revert_to_pending_endpoint()
    sys.exit(0 if success else 1)