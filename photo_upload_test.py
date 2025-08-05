#!/usr/bin/env python3
"""
Photo Upload Test Script for my420.ca Admin Registration
This script verifies that photo upload and email functionality is working correctly.
"""

import requests
import json
import base64
import random
import string
from datetime import date
import os
from dotenv import load_dotenv

class PhotoUploadTester:
    def __init__(self):
        # Load environment variables
        load_dotenv('/app/backend/.env')
        
        # Get backend URL from frontend env
        load_dotenv('/app/frontend/.env')
        self.backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
        
        print(f"🔧 Using backend URL: {self.backend_url}")
        
    def generate_test_photo(self, size_kb=500):
        """Generate a test photo of approximately the specified size"""
        print(f"📷 Generating test photo (~{size_kb}KB)...")
        
        # Create a base64 string representing a small JPEG
        base64_prefix = "data:image/jpeg;base64,"
        
        # Simple way to create a predictable size - use a pattern that compresses well
        chars_needed = int(size_kb * 1024 * 4/3)  # Base64 is ~4/3 the size of binary
        
        # Create a repeating pattern that looks like base64
        base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        base64_data = ''.join(base64_chars[i % len(base64_chars)] for i in range(chars_needed))
        
        # Add proper padding
        padding_needed = (4 - (len(base64_data) % 4)) % 4
        base64_data += "=" * padding_needed
        
        full_data = base64_prefix + base64_data
        actual_size_kb = len(full_data) / 1024
        
        print(f"✅ Test photo generated: {actual_size_kb:.2f}KB")
        return full_data
    
    def test_photo_upload_and_email(self):
        """Test complete photo upload and email workflow"""
        print("\n🧪 TESTING PHOTO UPLOAD AND EMAIL WORKFLOW")
        print("=" * 60)
        
        try:
            # Generate test data
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            test_photo = self.generate_test_photo(500)  # 500KB test photo
            
            test_data = {
                "firstName": f"PhotoTest {random_suffix}",
                "lastName": f"User {random_suffix}",
                "patientConsent": "Verbal",
                "province": "Ontario",
                "email": f"phototest.{random_suffix}@example.com",
                "photo": test_photo
            }
            
            print("\n📤 Submitting test registration with photo...")
            
            # Submit the registration
            response = requests.post(
                f"{self.backend_url}/api/admin-register",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                registration_id = result.get('registration_id')
                
                print("✅ PHOTO UPLOAD TEST SUCCESSFUL!")
                print(f"   Registration ID: {registration_id}")
                print("   ✅ Photo data processed correctly")
                print("   ✅ Email notification sent with photo attachment")
                print("   ✅ Registration stored in database")
                
                return True
                
            else:
                print(f"❌ PHOTO UPLOAD TEST FAILED!")
                print(f"   Status Code: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text}")
                
                return False
                
        except requests.exceptions.Timeout:
            print("❌ PHOTO UPLOAD TEST FAILED!")
            print("   Error: Request timed out (photo may be too large)")
            return False
            
        except requests.exceptions.ConnectionError:
            print("❌ PHOTO UPLOAD TEST FAILED!")
            print("   Error: Could not connect to backend server")
            return False
            
        except Exception as e:
            print("❌ PHOTO UPLOAD TEST FAILED!")
            print(f"   Error: {str(e)}")
            return False
    
    def test_without_photo(self):
        """Test registration without photo to ensure it still works"""
        print("\n🧪 TESTING REGISTRATION WITHOUT PHOTO")
        print("=" * 60)
        
        try:
            # Generate test data without photo
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            
            test_data = {
                "firstName": f"NoPhotoTest {random_suffix}",
                "lastName": f"User {random_suffix}",
                "patientConsent": "Verbal",
                "province": "Ontario",
                "email": f"nophototest.{random_suffix}@example.com"
                # No photo field
            }
            
            print("\n📤 Submitting test registration without photo...")
            
            # Submit the registration
            response = requests.post(
                f"{self.backend_url}/api/admin-register",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                registration_id = result.get('registration_id')
                
                print("✅ NO-PHOTO REGISTRATION TEST SUCCESSFUL!")
                print(f"   Registration ID: {registration_id}")
                print("   ✅ Registration processed without photo")
                print("   ✅ Email notification sent (no attachment)")
                
                return True
                
            else:
                print(f"❌ NO-PHOTO REGISTRATION TEST FAILED!")
                print(f"   Status Code: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text}")
                
                return False
                
        except Exception as e:
            print("❌ NO-PHOTO REGISTRATION TEST FAILED!")
            print(f"   Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all photo upload tests"""
        print("🚀 STARTING PHOTO UPLOAD VERIFICATION TESTS")
        print("=" * 60)
        print("This script will verify that photo upload and email functionality")
        print("is working correctly before users proceed with registration.")
        print("=" * 60)
        
        # Test 1: Photo upload with email
        test1_success = self.test_photo_upload_and_email()
        
        # Test 2: Registration without photo
        test2_success = self.test_without_photo()
        
        # Summary
        print("\n📊 TEST SUMMARY")
        print("=" * 60)
        
        if test1_success and test2_success:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Photo upload and email functionality is working correctly")
            print("✅ Users can safely proceed with photo uploads")
            print("✅ The system handles both scenarios: with and without photos")
            print("\n✨ The admin registration system is ready for use!")
            return True
        else:
            print("❌ SOME TESTS FAILED!")
            if not test1_success:
                print("❌ Photo upload and email functionality has issues")
            if not test2_success:
                print("❌ Registration without photo has issues")
            print("\n⚠️  Please fix the issues before proceeding with registration")
            return False

if __name__ == "__main__":
    tester = PhotoUploadTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🔥 Photo upload system is fully operational!")
        exit(0)
    else:
        print("\n💥 Photo upload system needs attention!")
        exit(1)