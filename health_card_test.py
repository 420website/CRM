import requests
import unittest
import json
import sys
import os
from dotenv import load_dotenv
import random
import string

class HealthCardCategorization:
    def __init__(self):
        # Initialize counters
        self.total_records = 0
        self.no_hc_count = 0
        self.invalid_hc_count = 0
        self.valid_hc_count = 0
        
        # Test data
        self.test_data = []
        
    def generate_test_data(self):
        """Generate test data with various health card formats"""
        # No health cards category
        no_health_cards = [
            None,
            "",
            "null",
            "none",
            "nan",
            "0000000000 NA",
            "0000000000",
            "NA",
            "0000000000NA"
        ]
        
        # Invalid health cards (10 digits but no suffix)
        invalid_health_cards = [
            "1234567890",
            "9876543210",
            "5555555555",
            "1111111111",
            "9999999999"
        ]
        
        # Valid health cards (10 digits + 2 letters)
        valid_health_cards = [
            "1234567890AB",
            "9876543210CD",
            "5555555555EF",
            "1111111111GH",
            "9999999999IJ"
        ]
        
        # Other formats (should be categorized as invalid)
        other_formats = [
            "12345",
            "123456789",
            "12345678901",
            "123456789A",
            "ABCDEFGHIJ",
            "1234567890ABC"
        ]
        
        # Create test records
        for hc in no_health_cards:
            self.test_data.append({"HC": hc, "expected_category": "no_hc"})
        
        for hc in invalid_health_cards:
            self.test_data.append({"HC": hc, "expected_category": "invalid_hc"})
        
        for hc in valid_health_cards:
            self.test_data.append({"HC": hc, "expected_category": "valid_hc"})
        
        for hc in other_formats:
            self.test_data.append({"HC": hc, "expected_category": "invalid_hc"})
        
        return self.test_data
    
    def categorize_health_card(self, hc):
        """Categorize a health card using the same logic as in server.py"""
        self.total_records += 1
        
        # Convert to string and strip whitespace
        hc_str = str(hc).strip() if hc is not None else ""
        
        # Check if no health card (empty, null, or 0000000000 NA patterns)
        if (not hc_str or 
            hc_str.lower() in ['', 'null', 'none', 'nan'] or
            hc_str == '0000000000 NA' or
            hc_str == '0000000000' or
            hc_str == 'NA' or
            hc_str == '0000000000NA'):
            self.no_hc_count += 1
            return "no_hc"
        else:
            # Has some health card data - check if it's invalid (missing 2-letter suffix)
            import re
            # Valid health card should have 10 digits followed by 2 letters (like 1234567890AB)
            # Invalid health card has numbers but missing the 2-letter suffix
            if re.match(r'^\d{10}$', hc_str):  # Exactly 10 digits with no letters
                self.invalid_hc_count += 1
                return "invalid_hc"
            elif re.match(r'^\d{10}[A-Za-z]{2}$', hc_str):  # 10 digits + 2 letters (valid format)
                self.valid_hc_count += 1
                return "valid_hc"
            else:
                # Other formats that don't match standard patterns - treat as invalid
                self.invalid_hc_count += 1
                return "invalid_hc"
    
    def test_categorization(self):
        """Test the health card categorization logic"""
        if not self.test_data:
            self.generate_test_data()
        
        results = {
            "total_tests": len(self.test_data),
            "passed_tests": 0,
            "failed_tests": 0,
            "failures": []
        }
        
        # Reset counters
        self.total_records = 0
        self.no_hc_count = 0
        self.invalid_hc_count = 0
        self.valid_hc_count = 0
        
        print("\n🔍 Testing Health Card Categorization Logic...")
        print("=" * 60)
        
        for i, test_case in enumerate(self.test_data):
            hc = test_case["HC"]
            expected = test_case["expected_category"]
            actual = self.categorize_health_card(hc)
            
            if actual == expected:
                results["passed_tests"] += 1
                print(f"✅ Test {i+1}: Health card '{hc}' correctly categorized as '{actual}'")
            else:
                results["failed_tests"] += 1
                failure = {
                    "health_card": hc,
                    "expected": expected,
                    "actual": actual
                }
                results["failures"].append(failure)
                print(f"❌ Test {i+1}: Health card '{hc}' incorrectly categorized as '{actual}' (expected '{expected}')")
        
        print("\n📊 Health Card Categorization Statistics:")
        print(f"Total records: {self.total_records}")
        print(f"No health cards: {self.no_hc_count}")
        print(f"Invalid health cards: {self.invalid_hc_count}")
        print(f"Valid health cards: {self.valid_hc_count}")
        
        # Verify that the counts are different
        if self.no_hc_count != self.invalid_hc_count:
            print(f"\n✅ VERIFICATION PASSED: 'No health cards' count ({self.no_hc_count}) is different from 'Invalid health cards' count ({self.invalid_hc_count})")
        else:
            print(f"\n❌ VERIFICATION FAILED: 'No health cards' count ({self.no_hc_count}) is the same as 'Invalid health cards' count ({self.invalid_hc_count})")
            results["failures"].append({
                "error": "Counts are the same",
                "no_hc_count": self.no_hc_count,
                "invalid_hc_count": self.invalid_hc_count
            })
        
        print("\n📊 Test Results:")
        print(f"Total tests: {results['total_tests']}")
        print(f"Passed tests: {results['passed_tests']}")
        print(f"Failed tests: {results['failed_tests']}")
        
        if results["failed_tests"] > 0:
            print("\n❌ Failed Tests:")
            for failure in results["failures"]:
                print(f"  - Health card: '{failure.get('health_card')}', Expected: '{failure.get('expected')}', Actual: '{failure.get('actual')}'")
        
        return results["failed_tests"] == 0

def test_claude_ai_context():
    """Test the Claude AI context generation with health card statistics"""
    # Load the frontend .env file to get the backend URL
    load_dotenv('/app/frontend/.env')
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return False
    
    print("\n🔍 Testing Claude AI Context with Health Card Statistics...")
    print("=" * 60)
    
    # Create a test message to send to the Claude AI endpoint
    test_message = "What percentage of clients have no health cards based on 0000000000 NA?"
    
    # Send the request to the Claude AI endpoint
    url = f"{backend_url}/api/claude-chat"
    headers = {'Content-Type': 'application/json'}
    data = {
        "message": test_message,
        "session_id": "test-session-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            ai_response = response_data.get("response", "")
            
            print(f"\n📝 Claude AI Response:")
            print("-" * 60)
            print(ai_response)
            print("-" * 60)
            
            # Check if the response contains information about both categories
            has_no_hc_info = "no health" in ai_response.lower()
            has_invalid_hc_info = "invalid health" in ai_response.lower()
            
            if has_no_hc_info and has_invalid_hc_info:
                print("\n✅ VERIFICATION PASSED: Claude AI response includes information about both 'no health cards' and 'invalid health cards'")
                return True
            else:
                print("\n❌ VERIFICATION FAILED: Claude AI response does not include information about both categories")
                if not has_no_hc_info:
                    print("  - Missing information about 'no health cards'")
                if not has_invalid_hc_info:
                    print("  - Missing information about 'invalid health cards'")
                return False
        else:
            print(f"\n❌ Error: Failed to get response from Claude AI endpoint (Status code: {response.status_code})")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response text: {response.text}")
            return False
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

def main():
    """Run all health card categorization tests"""
    print("🚀 Starting Health Card Categorization Tests")
    print("=" * 60)
    
    # Test the categorization logic
    categorization = HealthCardCategorization()
    categorization_success = categorization.test_categorization()
    
    # Test the Claude AI context
    context_success = test_claude_ai_context()
    
    # Overall success
    overall_success = categorization_success and context_success
    
    print("\n📊 Overall Test Results:")
    print(f"Categorization Logic: {'✅ PASSED' if categorization_success else '❌ FAILED'}")
    print(f"Claude AI Context: {'✅ PASSED' if context_success else '❌ FAILED'}")
    print(f"Overall: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())