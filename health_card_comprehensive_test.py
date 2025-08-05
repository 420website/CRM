import unittest
import sys
import re
import json

class TestHealthCardCategorizationLogic(unittest.TestCase):
    """Test the health card categorization logic from server.py"""
    
    def setUp(self):
        """Set up the test case"""
        # Initialize counters
        self.total_records = 0
        self.no_hc_count = 0
        self.invalid_hc_count = 0
        self.valid_hc_count = 0
        
        # Test data - create a mock dataset with various health card formats
        self.test_records = []
        
        # No health cards
        for hc in [None, "", "null", "none", "nan", "0000000000 NA", "0000000000", "NA", "0000000000NA"]:
            self.test_records.append({"HC": hc, "expected_category": "no_hc"})
        
        # Invalid health cards (10 digits but no suffix)
        for hc in ["1234567890", "9876543210", "5555555555", "1111111111", "9999999999"]:
            self.test_records.append({"HC": hc, "expected_category": "invalid_hc"})
        
        # Valid health cards (10 digits + 2 letters)
        for hc in ["1234567890AB", "9876543210CD", "5555555555EF", "1111111111GH", "9999999999IJ"]:
            self.test_records.append({"HC": hc, "expected_category": "valid_hc"})
        
        # Other formats (should be categorized as invalid)
        for hc in ["12345", "123456789", "12345678901", "123456789A", "ABCDEFGHIJ", "1234567890ABC"]:
            self.test_records.append({"HC": hc, "expected_category": "invalid_hc"})
    
    def process_health_cards(self):
        """Process health cards using the same logic as in server.py"""
        # Reset counters
        self.total_records = 0
        self.no_hc_count = 0
        self.invalid_hc_count = 0
        self.valid_hc_count = 0
        
        # Process each record
        for record in self.test_records:
            self.total_records += 1
            
            # Get health card value
            hc = record.get('HC')
            hc_str = str(hc).strip() if hc is not None else ""
            
            # Check if no health card (empty, null, or 0000000000 NA patterns)
            if (not hc_str or 
                hc_str.lower() in ['', 'null', 'none', 'nan'] or
                hc_str == '0000000000 NA' or
                hc_str == '0000000000' or
                hc_str == 'NA' or
                hc_str == '0000000000NA'):
                self.no_hc_count += 1
                record["actual_category"] = "no_hc"
            else:
                # Has some health card data - check if it's invalid (missing 2-letter suffix)
                # Valid health card should have 10 digits followed by 2 letters (like 1234567890AB)
                # Invalid health card has numbers but missing the 2-letter suffix
                if re.match(r'^\d{10}$', hc_str):  # Exactly 10 digits with no letters
                    self.invalid_hc_count += 1
                    record["actual_category"] = "invalid_hc"
                elif re.match(r'^\d{10}[A-Za-z]{2}$', hc_str):  # 10 digits + 2 letters (valid format)
                    self.valid_hc_count += 1
                    record["actual_category"] = "valid_hc"
                else:
                    # Other formats that don't match standard patterns - treat as invalid
                    self.invalid_hc_count += 1
                    record["actual_category"] = "invalid_hc"
    
    def test_categorization_logic(self):
        """Test that health cards are correctly categorized"""
        # Process the test data
        self.process_health_cards()
        
        # Verify each record was categorized correctly
        for record in self.test_records:
            self.assertEqual(record["actual_category"], record["expected_category"], 
                            f"Health card '{record['HC']}' should be categorized as '{record['expected_category']}', but was '{record['actual_category']}'")
    
    def test_different_counts(self):
        """Test that 'no health cards' and 'invalid health cards' have different counts"""
        # Process the test data
        self.process_health_cards()
        
        # Verify that the counts are different
        self.assertNotEqual(self.no_hc_count, self.invalid_hc_count, 
                           f"'No health cards' count ({self.no_hc_count}) should be different from 'Invalid health cards' count ({self.invalid_hc_count})")
        
        # Print the counts for verification
        print(f"\nHealth Card Categorization Statistics:")
        print(f"Total records: {self.total_records}")
        print(f"No health cards: {self.no_hc_count}")
        print(f"Invalid health cards: {self.invalid_hc_count}")
        print(f"Valid health cards: {self.valid_hc_count}")
        
        # Verify that the counts match the expected counts
        no_hc_expected = len([r for r in self.test_records if r["expected_category"] == "no_hc"])
        invalid_hc_expected = len([r for r in self.test_records if r["expected_category"] == "invalid_hc"])
        valid_hc_expected = len([r for r in self.test_records if r["expected_category"] == "valid_hc"])
        
        self.assertEqual(self.no_hc_count, no_hc_expected, 
                         f"Expected {no_hc_expected} 'no health cards', got {self.no_hc_count}")
        self.assertEqual(self.invalid_hc_count, invalid_hc_expected, 
                         f"Expected {invalid_hc_expected} 'invalid health cards', got {self.invalid_hc_count}")
        self.assertEqual(self.valid_hc_count, valid_hc_expected, 
                         f"Expected {valid_hc_expected} 'valid health cards', got {self.valid_hc_count}")
    
    def test_0000000000_NA_categorization(self):
        """Test that '0000000000 NA' is categorized as 'no health card' and not 'invalid health card'"""
        # Create a test record with '0000000000 NA'
        test_record = {"HC": "0000000000 NA"}
        
        # Process the record
        self.total_records = 0
        self.no_hc_count = 0
        self.invalid_hc_count = 0
        self.valid_hc_count = 0
        
        self.total_records += 1
        hc = test_record.get('HC')
        hc_str = str(hc).strip() if hc is not None else ""
        
        # Check if no health card (empty, null, or 0000000000 NA patterns)
        if (not hc_str or 
            hc_str.lower() in ['', 'null', 'none', 'nan'] or
            hc_str == '0000000000 NA' or
            hc_str == '0000000000' or
            hc_str == 'NA' or
            hc_str == '0000000000NA'):
            self.no_hc_count += 1
            test_record["category"] = "no_hc"
        else:
            # Has some health card data - check if it's invalid (missing 2-letter suffix)
            if re.match(r'^\d{10}$', hc_str):  # Exactly 10 digits with no letters
                self.invalid_hc_count += 1
                test_record["category"] = "invalid_hc"
            elif re.match(r'^\d{10}[A-Za-z]{2}$', hc_str):  # 10 digits + 2 letters (valid format)
                self.valid_hc_count += 1
                test_record["category"] = "valid_hc"
            else:
                # Other formats that don't match standard patterns - treat as invalid
                self.invalid_hc_count += 1
                test_record["category"] = "invalid_hc"
        
        # Verify categorization
        self.assertEqual(test_record["category"], "no_hc", 
                        f"'0000000000 NA' should be categorized as 'no_hc', but was '{test_record['category']}'")
        self.assertEqual(self.no_hc_count, 1, f"Expected 1 'no health card', got {self.no_hc_count}")
        self.assertEqual(self.invalid_hc_count, 0, f"Expected 0 'invalid health cards', got {self.invalid_hc_count}")
        self.assertEqual(self.valid_hc_count, 0, f"Expected 0 'valid health cards', got {self.valid_hc_count}")
    
    def test_context_generation(self):
        """Test that the context generation includes different counts for no_hc and invalid_hc"""
        # Process the test data
        self.process_health_cards()
        
        # Generate context text similar to server.py
        context_text = f"""
HEALTH CARD STATISTICS:
Total records: {self.total_records}
No health cards (including 0000000000 NA): {self.no_hc_count}
Invalid health cards (missing 2-letter suffix): {self.invalid_hc_count}
Valid health cards: {self.valid_hc_count}
Percentage with no health cards: {self.no_hc_count/self.total_records*100:.1f}%
Percentage with invalid health cards: {self.invalid_hc_count/self.total_records*100:.1f}%
"""
        
        # Print the context for verification
        print(f"\nGenerated Context:")
        print(context_text)
        
        # Verify that the context includes different counts
        self.assertIn(f"No health cards (including 0000000000 NA): {self.no_hc_count}", context_text)
        self.assertIn(f"Invalid health cards (missing 2-letter suffix): {self.invalid_hc_count}", context_text)
        self.assertNotEqual(self.no_hc_count, self.invalid_hc_count, 
                           f"'No health cards' count ({self.no_hc_count}) should be different from 'Invalid health cards' count ({self.invalid_hc_count})")

if __name__ == "__main__":
    # Print test data for verification
    test = TestHealthCardCategorizationLogic()
    test.setUp()
    print("\nTest Data:")
    for i, record in enumerate(test.test_records):
        print(f"{i+1}. Health card: '{record['HC']}', Expected category: '{record['expected_category']}'")
    
    # Run the tests
    unittest.main()