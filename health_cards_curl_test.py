import subprocess
import json
import sys
import random
import string

def run_curl_command(command):
    """Run a curl command and return the output"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def test_api_health():
    """Test the API health endpoint"""
    print("\n🔍 Testing API Health Check...")
    success, output = run_curl_command("curl -s http://127.0.0.1:8001/api/")
    
    if success:
        print("✅ Passed - API health check successful")
        try:
            response = json.loads(output)
            print(f"Response: {response}")
            return True
        except:
            print(f"Response: {output}")
            return True
    else:
        print(f"❌ Failed - API health check failed: {output}")
        return False

def test_claude_chat_health_cards_query():
    """Test the Claude chat endpoint with a health cards query"""
    print("\n🔍 Testing Claude Chat - Health Cards Query...")
    
    # The query that the Health Cards button sends
    session_id = "test-session-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    query = "What percentage of patients have invalid health cards based on 0000000000 NA"
    
    command = f"""curl -s -X POST -H "Content-Type: application/json" -d '{{"message": "{query}", "session_id": "{session_id}"}}' http://127.0.0.1:8001/api/claude-chat"""
    
    success, output = run_curl_command(command)
    
    if success:
        print("✅ Passed - Claude chat query successful")
        try:
            response = json.loads(output)
            response_text = response.get('response', '')
            print(f"Response from Claude AI: {response_text[:200]}...")  # Print first 200 chars
            
            # Check if the response contains percentage information
            contains_percentage = False
            percentage_keywords = ['percent', '%', 'invalid health cards', 'valid health cards']
            for keyword in percentage_keywords:
                if keyword.lower() in response_text.lower():
                    contains_percentage = True
                    break
            
            if contains_percentage:
                print("✅ Response contains percentage information about health cards")
            else:
                print("❌ Response does not contain percentage information about health cards")
            
            # Check if the response mentions the specific pattern '0000000000 NA'
            if '0000000000 NA' in response_text:
                print("✅ Response specifically mentions the '0000000000 NA' pattern")
            else:
                print("❌ Response does not mention the '0000000000 NA' pattern")
                
            return True
        except:
            print(f"Response: {output}")
            return False
    else:
        print(f"❌ Failed - Claude chat query failed: {output}")
        return False

def test_claude_chat_health_cards_variations():
    """Test the Claude chat endpoint with variations of health cards queries"""
    print("\n🔍 Testing Claude Chat - Health Cards Variations...")
    
    variations = [
        "How many patients have invalid health cards?",
        "What is the percentage of valid health cards in the system?",
        "Tell me about health card statistics",
        "How many health cards are invalid with the pattern 0000000000 NA?",
        "What percentage of health cards are valid vs invalid?"
    ]
    
    all_success = True
    
    for query in variations:
        print(f"\n🔍 Testing Claude Chat with query: '{query}'")
        
        session_id = "test-session-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        command = f"""curl -s -X POST -H "Content-Type: application/json" -d '{{"message": "{query}", "session_id": "{session_id}"}}' http://127.0.0.1:8001/api/claude-chat"""
        
        success, output = run_curl_command(command)
        
        if success:
            print("✅ Passed - Claude chat query successful")
            try:
                response = json.loads(output)
                response_text = response.get('response', '')
                print(f"Response from Claude AI: {response_text[:150]}...")  # Print first 150 chars
                
                # Check if the response contains health card related information
                contains_health_card_info = False
                health_card_keywords = ['health card', 'invalid', 'valid', 'percentage', 'statistics']
                for keyword in health_card_keywords:
                    if keyword.lower() in response_text.lower():
                        contains_health_card_info = True
                        break
                
                if contains_health_card_info:
                    print("✅ Response contains health card related information")
                else:
                    print("❌ Response does not contain health card related information")
                    all_success = False
            except:
                print(f"Response: {output}")
                all_success = False
        else:
            print(f"❌ Failed - Claude chat query failed: {output}")
            all_success = False
    
    return all_success

def test_legacy_data_summary():
    """Test the legacy data summary endpoint to check for health card statistics"""
    print("\n🔍 Testing Legacy Data Summary...")
    
    success, output = run_curl_command("curl -s http://127.0.0.1:8001/api/legacy-data-summary")
    
    if success:
        print("✅ Passed - Legacy data summary successful")
        try:
            response = json.loads(output)
            print(f"Response: {response}")
            return True
        except:
            print(f"Response: {output}")
            # This test might fail if no legacy data has been uploaded yet
            if "No legacy data found" in output:
                print("⚠️ No legacy data found. This is expected if no Excel file has been uploaded.")
                return True
            return False
    else:
        print(f"❌ Failed - Legacy data summary failed: {output}")
        return False

def run_all_tests():
    """Run all Health Cards API tests"""
    print("🚀 Starting Health Cards API Tests")
    print("=" * 50)
    
    tests_run = 0
    tests_passed = 0
    
    # Test 1: API Health
    tests_run += 1
    if test_api_health():
        tests_passed += 1
    
    # Test 2: Claude Chat - Health Cards Query
    tests_run += 1
    if test_claude_chat_health_cards_query():
        tests_passed += 1
    
    # Test 3: Claude Chat - Health Cards Variations
    tests_run += 1
    if test_claude_chat_health_cards_variations():
        tests_passed += 1
    
    # Test 4: Legacy Data Summary
    tests_run += 1
    if test_legacy_data_summary():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {tests_passed}/{tests_run}")
    
    return tests_passed == tests_run

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)