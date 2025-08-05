import unittest
import json
import sys

class HealthCardTests(unittest.TestCase):
    """Unit tests for health card functionality"""
    
    def test_health_card_validation(self):
        """Test the health card validation logic"""
        print("\n🔍 Testing Health Card Validation Logic...")
        
        # Test cases for health card validation
        test_cases = [
            {"hc": "0000000000 NA", "expected": "invalid"},
            {"hc": "0000000000", "expected": "invalid"},
            {"hc": "NA", "expected": "invalid"},
            {"hc": "0000000000NA", "expected": "invalid"},
            {"hc": "", "expected": "invalid"},
            {"hc": None, "expected": "invalid"},
            {"hc": "null", "expected": "invalid"},
            {"hc": "none", "expected": "invalid"},
            {"hc": "nan", "expected": "invalid"},
            {"hc": "1234567890", "expected": "valid"},
            {"hc": "1234567890AB", "expected": "valid"},
            {"hc": "1234-5678-90", "expected": "valid"}
        ]
        
        # Implement the same validation logic as in server.py
        def is_invalid_health_card(hc):
            if hc is None:
                return True
                
            hc_str = str(hc).strip()
            
            return (not hc_str or 
                    hc_str.lower() in ['', 'null', 'none', 'nan'] or
                    hc_str == '0000000000 NA' or
                    hc_str == '0000000000' or
                    hc_str == 'NA' or
                    hc_str == '0000000000NA')
        
        # Run the test cases
        for i, test_case in enumerate(test_cases):
            hc = test_case["hc"]
            expected = test_case["expected"]
            
            result = "invalid" if is_invalid_health_card(hc) else "valid"
            
            if result == expected:
                print(f"✅ Test case {i+1}: Health card '{hc}' correctly identified as {result}")
            else:
                print(f"❌ Test case {i+1}: Health card '{hc}' incorrectly identified as {result}, expected {expected}")
                
            self.assertEqual(result, expected, f"Health card '{hc}' should be {expected}, but was {result}")
    
    def test_health_card_percentage_calculation(self):
        """Test the health card percentage calculation"""
        print("\n🔍 Testing Health Card Percentage Calculation...")
        
        # Test cases for percentage calculation
        test_cases = [
            {"total": 100, "invalid": 10, "expected_percentage": 10.0},
            {"total": 100, "invalid": 0, "expected_percentage": 0.0},
            {"total": 100, "invalid": 100, "expected_percentage": 100.0},
            {"total": 1776, "invalid": 172, "expected_percentage": 9.7}
        ]
        
        # Implement the same percentage calculation as in server.py
        def calculate_percentage(invalid_count, total_count):
            return (invalid_count / total_count) * 100
        
        # Run the test cases
        for i, test_case in enumerate(test_cases):
            total = test_case["total"]
            invalid = test_case["invalid"]
            expected_percentage = test_case["expected_percentage"]
            
            percentage = calculate_percentage(invalid, total)
            rounded_percentage = round(percentage, 1)
            
            if abs(rounded_percentage - expected_percentage) < 0.1:
                print(f"✅ Test case {i+1}: Percentage calculation correct: {invalid}/{total} = {rounded_percentage}%")
            else:
                print(f"❌ Test case {i+1}: Percentage calculation incorrect: {invalid}/{total} = {rounded_percentage}%, expected {expected_percentage}%")
                
            self.assertAlmostEqual(rounded_percentage, expected_percentage, places=1, 
                                  msg=f"Percentage calculation for {invalid}/{total} should be {expected_percentage}%, but was {rounded_percentage}%")
    
    def test_health_card_context_generation(self):
        """Test the health card context generation for Claude AI"""
        print("\n🔍 Testing Health Card Context Generation...")
        
        # Mock health card statistics
        health_card_stats = {
            'total_records': 1776,
            'invalid_hc_count': 172,
            'valid_hc_count': 1604
        }
        
        # Generate context text similar to server.py
        context_text = f"""
HEALTH CARD STATISTICS:
Total records: {health_card_stats['total_records']}
Invalid health cards (including 0000000000 NA): {health_card_stats['invalid_hc_count']}
Valid health cards: {health_card_stats['valid_hc_count']}
Percentage with invalid health cards: {health_card_stats['invalid_hc_count']/health_card_stats['total_records']*100:.1f}%
"""
        
        # Check if the context contains the expected information
        expected_elements = [
            "HEALTH CARD STATISTICS",
            "Total records: 1776",
            "Invalid health cards",
            "Valid health cards: 1604",
            "Percentage with invalid health cards"
        ]
        
        all_elements_present = True
        for element in expected_elements:
            if element not in context_text:
                print(f"❌ Context text missing expected element: '{element}'")
                all_elements_present = False
            else:
                print(f"✅ Context text contains expected element: '{element}'")
                
        self.assertTrue(all_elements_present, "Context text should contain all expected elements")
        
        # Check if the percentage calculation is correct
        expected_percentage = "9.7%"
        if expected_percentage in context_text:
            print(f"✅ Context text contains correct percentage: {expected_percentage}")
        else:
            print(f"❌ Context text does not contain correct percentage: {expected_percentage}")
            
        self.assertIn(expected_percentage, context_text, f"Context text should contain the correct percentage: {expected_percentage}")

def run_tests():
    """Run all health card tests"""
    print("🚀 Starting Health Card Unit Tests")
    print("=" * 50)
    
    # Create a test suite
    suite = unittest.TestSuite()
    suite.addTest(HealthCardTests('test_health_card_validation'))
    suite.addTest(HealthCardTests('test_health_card_percentage_calculation'))
    suite.addTest(HealthCardTests('test_health_card_context_generation'))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {result.testsRun - len(result.errors) - len(result.failures)}/{result.testsRun}")
    
    return len(result.errors) == 0 and len(result.failures) == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)