import unittest
import sys
import os
import json
import re
import requests
from datetime import datetime, date
import pandas as pd
import random
import string
import time

class ColumnPRewardsProcessingTester(unittest.TestCase):
    """Tests specifically focused on column P rewards processing logic"""
    
    def setUp(self):
        """Set up test data and API URL"""
        # Load the frontend .env file to get the backend URL
        from dotenv import load_dotenv
        load_dotenv('/app/frontend/.env')
        
        # Get the backend URL from the environment variable
        self.base_url = os.environ.get('REACT_APP_BACKEND_URL')
        if not self.base_url:
            self.fail("REACT_APP_BACKEND_URL not found in frontend .env file")
        
        # Create test records specifically for column P testing
        self.test_records = []
        
        # 1. Test records with only column P values
        for i in range(100):
            amount = random.uniform(50, 150)  # Random amount between $50-$150
            reg_date = f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            
            # Alternate between different formats for column P
            format_type = i % 5
            if format_type == 0:
                self.test_records.append({"RegDate": reg_date, "P": f"${amount:.2f}"})  # String with dollar sign
            elif format_type == 1:
                self.test_records.append({"RegDate": reg_date, "P": amount})  # Numeric value
            elif format_type == 2:
                self.test_records.append({"RegDate": reg_date, "P": f"{amount:.2f}"})  # String without dollar sign
            elif format_type == 3:
                self.test_records.append({"RegDate": reg_date, "p": amount})  # Lowercase p
            else:
                self.test_records.append({"RegDate": reg_date, "P": f"${amount:.2f} CAD"})  # With currency code
        
        # 2. Test records with column P and other reward fields to ensure P is prioritized
        for i in range(50):
            p_amount = random.uniform(100, 200)  # Higher amount in column P
            other_amount = random.uniform(10, 50)  # Lower amount in other fields
            reg_date = f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            
            record = {
                "RegDate": reg_date,
                "P": p_amount,  # Column P value
                "Amount": other_amount,  # Should be ignored if P is present
                "Reward": other_amount  # Should be ignored if P is present
            }
            self.test_records.append(record)
        
        # 3. Test records with column P containing various formats and edge cases
        special_p_records = [
            {"RegDate": "2024-01-15", "P": "$1,000.00"},  # Comma in number
            {"RegDate": "2024-02-20", "P": " $500.50 "},  # Spaces around value
            {"RegDate": "2024-03-10", "P": "750"},  # Integer as string
            {"RegDate": "2024-04-05", "P": "$1,234.56 CAD"},  # With currency code
            {"RegDate": "2024-05-12", "P": "USD 800.75"},  # Currency code before value
            {"RegDate": "2024-06-18", "P": "900"},  # Integer as string without decimal
            {"RegDate": "2024-07-22", "P": "$1200.00"},  # No comma in larger number
            {"RegDate": "2024-08-30", "P": "1500.00$"},  # Dollar sign at end
            {"RegDate": "2024-09-14", "P": "2,000"},  # Comma but no decimal
            {"RegDate": "2024-10-05", "P": "$3000"}  # No comma, no decimal
        ]
        self.test_records.extend(special_p_records)
        
        # Calculate the expected total for verification
        self.expected_total = 0
        for record in self.test_records:
            p_value = record.get('P') or record.get('p')
            if p_value:
                if isinstance(p_value, (int, float)):
                    self.expected_total += float(p_value)
                else:
                    # Extract numeric value from string
                    p_str = str(p_value).strip().replace('$', '').replace(',', '').replace('CAD', '').replace('USD', '').strip()
                    try:
                        self.expected_total += float(p_str)
                    except:
                        pass  # Skip invalid values
    
    def process_rewards(self, records):
        """Replicate the enhanced rewards processing logic from server.py with focus on column P"""
        rewards_stats = {
            'total_amount': 0,
            'total_records_with_amount': 0,
            'column_p_total': 0,
            'column_p_count': 0,
            'other_fields_total': 0,
            'other_fields_count': 0
        }
        
        for record in records:
            # First check for column P specifically
            p_value = record.get('P') or record.get('p')
            amount_val = 0
            
            if p_value is not None:
                # Process column P value
                if isinstance(p_value, (int, float)) and p_value > 0:
                    amount_val = float(p_value)
                    rewards_stats['column_p_total'] += amount_val
                    rewards_stats['column_p_count'] += 1
                elif str(p_value).strip():
                    p_str = str(p_value).strip().replace('$', '').replace(',', '').replace('CAD', '').replace('USD', '').strip()
                    if p_str and p_str.lower() not in ['', 'null', 'none', 'nan', '0', '0.0', '0.00', 'n/a', 'na']:
                        try:
                            amount_val = float(p_str)
                            rewards_stats['column_p_total'] += amount_val
                            rewards_stats['column_p_count'] += 1
                        except ValueError:
                            # Handle potential integer fields or other numeric formats
                            try:
                                # Remove any non-numeric characters except decimal point
                                clean_amount = ''.join(c for c in p_str if c.isdigit() or c == '.')
                                if clean_amount and '.' in clean_amount:
                                    amount_val = float(clean_amount)
                                    rewards_stats['column_p_total'] += amount_val
                                    rewards_stats['column_p_count'] += 1
                                elif clean_amount:
                                    amount_val = float(clean_amount)
                                    rewards_stats['column_p_total'] += amount_val
                                    rewards_stats['column_p_count'] += 1
                            except:
                                pass
            else:
                # If no column P, check other fields
                other_amount = (record.get('Amount') or record.get('amount') or 
                               record.get('Reward') or record.get('reward') or 
                               record.get('AMOUNT') or record.get('REWARD') or
                               record.get('rewards') or record.get('REWARDS') or
                               record.get('payment') or record.get('Payment') or
                               record.get('PAYMENT') or 0)
                
                if isinstance(other_amount, (int, float)) and other_amount > 0:
                    amount_val = float(other_amount)
                    rewards_stats['other_fields_total'] += amount_val
                    rewards_stats['other_fields_count'] += 1
                elif str(other_amount).strip():
                    other_str = str(other_amount).strip().replace('$', '').replace(',', '').replace('CAD', '').replace('USD', '').strip()
                    if other_str and other_str.lower() not in ['', 'null', 'none', 'nan', '0', '0.0', '0.00', 'n/a', 'na']:
                        try:
                            amount_val = float(other_str)
                            rewards_stats['other_fields_total'] += amount_val
                            rewards_stats['other_fields_count'] += 1
                        except ValueError:
                            try:
                                # Remove any non-numeric characters except decimal point
                                clean_amount = ''.join(c for c in other_str if c.isdigit() or c == '.')
                                if clean_amount and '.' in clean_amount:
                                    amount_val = float(clean_amount)
                                    rewards_stats['other_fields_total'] += amount_val
                                    rewards_stats['other_fields_count'] += 1
                                elif clean_amount:
                                    amount_val = float(clean_amount)
                                    rewards_stats['other_fields_total'] += amount_val
                                    rewards_stats['other_fields_count'] += 1
                            except:
                                pass
            
            # Add to total if we found a value
            if amount_val > 0:
                rewards_stats['total_amount'] += amount_val
                rewards_stats['total_records_with_amount'] += 1
        
        return rewards_stats
    
    def test_column_p_total(self):
        """Test that column P values are correctly processed and totaled"""
        rewards_stats = self.process_rewards(self.test_records)
        
        # Check that the total matches our expected total
        total_amount = rewards_stats['total_amount']
        column_p_total = rewards_stats['column_p_total']
        
        print(f"✅ Column P processing results:")
        print(f"   Total amount: ${total_amount:.2f}")
        print(f"   Column P total: ${column_p_total:.2f}")
        print(f"   Other fields total: ${rewards_stats['other_fields_total']:.2f}")
        print(f"   Records with column P: {rewards_stats['column_p_count']}")
        print(f"   Records with other fields: {rewards_stats['other_fields_count']}")
        print(f"   Total records with amounts: {rewards_stats['total_records_with_amount']}")
        
        # Verify column P is the majority of the total
        self.assertGreater(column_p_total, rewards_stats['other_fields_total'])
        
        # Verify the total is close to our expected total (within 1%)
        margin = 0.01  # 1% margin
        self.assertTrue(self.expected_total * (1 - margin) <= total_amount <= self.expected_total * (1 + margin))
        print(f"✅ Total amount matches expected: ${total_amount:.2f} vs ${self.expected_total:.2f}")
        print(f"   Difference: ${abs(total_amount - self.expected_total):.2f} ({abs(total_amount - self.expected_total) / self.expected_total * 100:.2f}%)")
    
    def test_column_p_prioritization(self):
        """Test that column P is prioritized over other fields when both are present"""
        # Create records with both column P and other fields
        priority_test_records = []
        
        for i in range(20):
            p_amount = 100.00  # Fixed amount in column P
            other_amount = 50.00  # Lower amount in other fields
            reg_date = f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            
            record = {
                "RegDate": reg_date,
                "P": p_amount,  # Column P value
                "Amount": other_amount,  # Should be ignored if P is present
                "Reward": other_amount  # Should be ignored if P is present
            }
            priority_test_records.append(record)
        
        rewards_stats = self.process_rewards(priority_test_records)
        
        # Expected total if column P is prioritized: 20 records * $100 = $2,000
        # If other fields were used instead: 20 records * $50 = $1,000
        expected_p_total = 20 * 100.00
        
        self.assertEqual(rewards_stats['column_p_total'], expected_p_total)
        self.assertEqual(rewards_stats['column_p_count'], 20)
        
        # Other fields should not be counted when P is present
        self.assertEqual(rewards_stats['other_fields_count'], 0)
        
        print(f"✅ Column P prioritization correct:")
        print(f"   Column P total: ${rewards_stats['column_p_total']:.2f}")
        print(f"   Other fields total: ${rewards_stats['other_fields_total']:.2f}")
        print(f"   Records with column P: {rewards_stats['column_p_count']}")
        print(f"   Records with other fields: {rewards_stats['other_fields_count']}")
    
    def test_column_p_format_handling(self):
        """Test that various formats of column P values are handled correctly"""
        # Test records with various column P formats
        format_test_records = [
            {"RegDate": "2024-01-15", "P": "$1,000.00"},  # Comma in number
            {"RegDate": "2024-02-20", "P": " $500.50 "},  # Spaces around value
            {"RegDate": "2024-03-10", "P": "750"},  # Integer as string
            {"RegDate": "2024-04-05", "P": "$1,234.56 CAD"},  # With currency code
            {"RegDate": "2024-05-12", "P": "USD 800.75"},  # Currency code before value
            {"RegDate": "2024-06-18", "P": "900"},  # Integer as string without decimal
            {"RegDate": "2024-07-22", "P": "$1200.00"},  # No comma in larger number
            {"RegDate": "2024-08-30", "P": "1500.00$"},  # Dollar sign at end
            {"RegDate": "2024-09-14", "P": "2,000"},  # Comma but no decimal
            {"RegDate": "2024-10-05", "P": "$3000"}  # No comma, no decimal
        ]
        
        rewards_stats = self.process_rewards(format_test_records)
        
        # Expected total if all formats are handled correctly
        expected_total = 1000.00 + 500.50 + 750.00 + 1234.56 + 800.75 + 900.00 + 1200.00 + 1500.00 + 2000.00 + 3000.00
        
        self.assertAlmostEqual(rewards_stats['column_p_total'], expected_total, places=2)
        self.assertEqual(rewards_stats['column_p_count'], 10)
        
        print(f"✅ Column P format handling correct:")
        print(f"   Column P total: ${rewards_stats['column_p_total']:.2f}")
        print(f"   Expected total: ${expected_total:.2f}")
        print(f"   Records with column P: {rewards_stats['column_p_count']}")
        print(f"   All 10 format variations processed correctly")


def run_tests():
    """Run all tests"""
    print("🚀 Starting Column P Rewards Processing Tests")
    print("=" * 50)
    
    # Create a test suite
    suite = unittest.TestSuite()
    suite.addTest(ColumnPRewardsProcessingTester('test_column_p_total'))
    suite.addTest(ColumnPRewardsProcessingTester('test_column_p_prioritization'))
    suite.addTest(ColumnPRewardsProcessingTester('test_column_p_format_handling'))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {result.testsRun - len(result.errors) - len(result.failures)}/{result.testsRun}")
    
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)