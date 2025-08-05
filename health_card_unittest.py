import unittest
import sys
import re

class TestHealthCardCategorization(unittest.TestCase):
    """Test the health card categorization logic"""
    
    def setUp(self):
        """Set up the test case"""
        # Initialize counters
        self.total_records = 0
        self.no_hc_count = 0
        self.invalid_hc_count = 0
        self.valid_hc_count = 0
        
        # Test data
        self.no_health_cards = [
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
        
        self.invalid_health_cards = [
            "1234567890",
            "9876543210",
            "5555555555",
            "1111111111",
            "9999999999",
            "12345",
            "123456789",
            "12345678901",
            "123456789A",
            "ABCDEFGHIJ",
            "1234567890ABC"
        ]
        
        self.valid_health_cards = [
            "1234567890AB",
            "9876543210CD",
            "5555555555EF",
            "1111111111GH",
            "9999999999IJ"
        ]
    
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
    
    def test_no_health_cards_categorization(self):
        """Test that 'no health cards' are correctly categorized"""
        for hc in self.no_health_cards:
            category = self.categorize_health_card(hc)
            self.assertEqual(category, "no_hc", f"Health card '{hc}' should be categorized as 'no_hc'")
    
    def test_invalid_health_cards_categorization(self):
        """Test that 'invalid health cards' are correctly categorized"""
        for hc in self.invalid_health_cards:
            category = self.categorize_health_card(hc)
            self.assertEqual(category, "invalid_hc", f"Health card '{hc}' should be categorized as 'invalid_hc'")
    
    def test_valid_health_cards_categorization(self):
        """Test that 'valid health cards' are correctly categorized"""
        for hc in self.valid_health_cards:
            category = self.categorize_health_card(hc)
            self.assertEqual(category, "valid_hc", f"Health card '{hc}' should be categorized as 'valid_hc'")
    
    def test_different_counts(self):
        """Test that 'no health cards' and 'invalid health cards' have different counts"""
        # Reset counters
        self.total_records = 0
        self.no_hc_count = 0
        self.invalid_hc_count = 0
        self.valid_hc_count = 0
        
        # Process all test data
        for hc in self.no_health_cards + self.invalid_health_cards + self.valid_health_cards:
            self.categorize_health_card(hc)
        
        # Verify counts
        self.assertEqual(self.no_hc_count, len(self.no_health_cards), 
                         f"Expected {len(self.no_health_cards)} 'no health cards', got {self.no_hc_count}")
        self.assertEqual(self.invalid_hc_count, len(self.invalid_health_cards), 
                         f"Expected {len(self.invalid_health_cards)} 'invalid health cards', got {self.invalid_hc_count}")
        self.assertEqual(self.valid_hc_count, len(self.valid_health_cards), 
                         f"Expected {len(self.valid_health_cards)} 'valid health cards', got {self.valid_hc_count}")
        
        # Verify that the counts are different
        self.assertNotEqual(self.no_hc_count, self.invalid_hc_count, 
                           "'No health cards' count should be different from 'Invalid health cards' count")
    
    def test_0000000000_NA_categorization(self):
        """Test that '0000000000 NA' is categorized as 'no health card' and not 'invalid health card'"""
        # Reset counters
        self.total_records = 0
        self.no_hc_count = 0
        self.invalid_hc_count = 0
        self.valid_hc_count = 0
        
        # Process the test case
        category = self.categorize_health_card("0000000000 NA")
        
        # Verify categorization
        self.assertEqual(category, "no_hc", "'0000000000 NA' should be categorized as 'no_hc'")
        self.assertEqual(self.no_hc_count, 1, "Expected 1 'no health card', got {self.no_hc_count}")
        self.assertEqual(self.invalid_hc_count, 0, "Expected 0 'invalid health cards', got {self.invalid_hc_count}")
        self.assertEqual(self.valid_hc_count, 0, "Expected 0 'valid health cards', got {self.valid_hc_count}")

if __name__ == "__main__":
    unittest.main()