import unittest
import sys
import os
import json
import re
from datetime import datetime, date
import pandas as pd

class RewardsProcessingUnitTest(unittest.TestCase):
    """Unit tests for the rewards processing logic"""
    
    def setUp(self):
        """Set up test data"""
        # Create sample records with various reward/amount formats
        self.test_records = [
            # Record with Amount as string with dollar sign
            {"RegDate": "2024-01-15", "Amount": "$100.00", "Reward": None},
            # Record with Amount as string without dollar sign
            {"RegDate": "2024-02-20", "Amount": "150.50", "Reward": None},
            # Record with Amount as integer
            {"RegDate": "2024-03-10", "Amount": 200, "Reward": None},
            # Record with Amount as float
            {"RegDate": "2024-04-05", "Amount": 250.75, "Reward": None},
            # Record with Reward field instead of Amount
            {"RegDate": "2024-05-12", "Amount": None, "Reward": "$300.00"},
            # Record with Reward field as integer
            {"RegDate": "2024-06-18", "Amount": None, "Reward": 350},
            # Record with AMOUNT (uppercase) field
            {"RegDate": "2024-07-22", "AMOUNT": "$400.00", "Amount": None, "Reward": None},
            # Record with REWARD (uppercase) field
            {"RegDate": "2024-08-30", "Amount": None, "Reward": None, "REWARD": "450.25"},
            # Record with amount field containing commas
            {"RegDate": "2024-09-14", "Amount": "$1,500.00", "Reward": None},
            # Record with reward field containing spaces
            {"RegDate": "2024-10-05", "Amount": None, "Reward": " 550.75 "},
            # Record with 2025 date
            {"RegDate": "2025-01-20", "Amount": "$600.00", "Reward": None},
            # Record with 2025 date and integer amount
            {"RegDate": "2025-02-15", "Amount": 650, "Reward": None},
            # Record with 2025 date and reward field
            {"RegDate": "2025-03-10", "Amount": None, "Reward": "$700.00"},
            # Record with no amount or reward
            {"RegDate": "2025-04-05", "Amount": None, "Reward": None},
            # Record with zero amount
            {"RegDate": "2025-05-12", "Amount": "0.00", "Reward": None},
            # Record with invalid amount format (should be skipped)
            {"RegDate": "2025-06-18", "Amount": "invalid", "Reward": None},
            # Record with null amount string
            {"RegDate": "2025-07-22", "Amount": "null", "Reward": None},
            # Record with none amount string
            {"RegDate": "2025-08-30", "Amount": "none", "Reward": None},
            # Record with nan amount string
            {"RegDate": "2025-09-14", "Amount": "nan", "Reward": None},
            # Record with amount as string "0"
            {"RegDate": "2025-10-05", "Amount": "0", "Reward": None}
        ]
    
    def process_rewards(self, records):
        """Replicate the rewards processing logic from server.py"""
        rewards_stats = {
            'total_amount': 0,
            'total_records_with_amount': 0,
            'monthly_totals_2024': {},
            'monthly_totals_2025': {},
            'yearly_totals': {'2024': 0, '2025': 0}
        }
        
        for record in records:
            # Check rewards/amount - be more thorough in capturing all reward data
            amount = record.get('Amount') or record.get('amount') or record.get('Reward') or record.get('reward') or record.get('AMOUNT') or record.get('REWARD') or 0
            try:
                # Convert to float, handling various formats
                amount_val = 0
                if amount is not None and str(amount).strip():
                    amount_str = str(amount).strip().replace('$', '').replace(',', '').replace(' ', '')
                    if amount_str and amount_str.lower() not in ['', 'null', 'none', 'nan', '0', '0.0', '0.00']:
                        try:
                            amount_val = float(amount_str)
                        except ValueError:
                            # Handle potential integer fields or other numeric formats
                            try:
                                amount_val = float(int(amount_str))
                            except:
                                pass
                
                # Also check if amount is already a number
                elif isinstance(amount, (int, float)) and amount > 0:
                    amount_val = float(amount)
                
                if amount_val > 0:
                    rewards_stats['total_amount'] += amount_val
                    rewards_stats['total_records_with_amount'] += 1
                    
                    # Get date for monthly/yearly breakdown
                    reg_date = record.get('RegDate') or record.get('regDate') or record.get('REGDATE')
                    if reg_date and str(reg_date).strip():
                        try:
                            year = None
                            month_key = None
                            
                            if isinstance(reg_date, str) and len(reg_date) >= 7:
                                year = reg_date[:4]
                                month_key = reg_date[:7]  # YYYY-MM
                            else:
                                parsed_date = pd.to_datetime(reg_date, errors='coerce')
                                if pd.notna(parsed_date):
                                    year = parsed_date.strftime('%Y')
                                    month_key = parsed_date.strftime('%Y-%m')
                            
                            # Add to yearly totals
                            if year in ['2024', '2025']:
                                rewards_stats['yearly_totals'][year] += amount_val
                                
                                # Add to monthly totals
                                if year == '2024':
                                    rewards_stats['monthly_totals_2024'][month_key] = rewards_stats['monthly_totals_2024'].get(month_key, 0) + amount_val
                                elif year == '2025':
                                    rewards_stats['monthly_totals_2025'][month_key] = rewards_stats['monthly_totals_2025'].get(month_key, 0) + amount_val
                        except:
                            pass  # Skip invalid dates
            except Exception as e:
                print(f"Error processing amount {amount}: {str(e)}")
                pass  # Skip invalid amounts
        
        return rewards_stats
    
    def test_total_amount_calculation(self):
        """Test that the total amount is calculated correctly"""
        rewards_stats = self.process_rewards(self.test_records)
        
        # Calculate expected total (sum of all valid amounts)
        expected_total = 100.00 + 150.50 + 200.00 + 250.75 + 300.00 + 350.00 + 400.00 + 450.25 + 1500.00 + 550.75 + 600.00 + 650.00 + 700.00
        
        self.assertAlmostEqual(rewards_stats['total_amount'], expected_total, places=2)
        print(f"✅ Total amount calculation correct: ${rewards_stats['total_amount']:.2f}")
    
    def test_records_with_amount_count(self):
        """Test that the count of records with amounts is correct"""
        rewards_stats = self.process_rewards(self.test_records)
        
        # Expected count (number of records with valid amounts)
        expected_count = 13  # 13 records have valid amounts
        
        self.assertEqual(rewards_stats['total_records_with_amount'], expected_count)
        print(f"✅ Records with amount count correct: {rewards_stats['total_records_with_amount']}")
    
    def test_yearly_totals(self):
        """Test that the yearly totals are calculated correctly"""
        rewards_stats = self.process_rewards(self.test_records)
        
        # Calculate expected yearly totals
        expected_2024_total = 100.00 + 150.50 + 200.00 + 250.75 + 300.00 + 350.00 + 400.00 + 450.25 + 1500.00 + 550.75
        expected_2025_total = 600.00 + 650.00 + 700.00
        
        self.assertAlmostEqual(rewards_stats['yearly_totals']['2024'], expected_2024_total, places=2)
        self.assertAlmostEqual(rewards_stats['yearly_totals']['2025'], expected_2025_total, places=2)
        print(f"✅ 2024 total correct: ${rewards_stats['yearly_totals']['2024']:.2f}")
        print(f"✅ 2025 total correct: ${rewards_stats['yearly_totals']['2025']:.2f}")
    
    def test_monthly_totals(self):
        """Test that the monthly totals are calculated correctly"""
        rewards_stats = self.process_rewards(self.test_records)
        
        # Check a few monthly totals
        self.assertAlmostEqual(rewards_stats['monthly_totals_2024'].get('2024-01', 0), 100.00, places=2)
        self.assertAlmostEqual(rewards_stats['monthly_totals_2024'].get('2024-09', 0), 1500.00, places=2)
        self.assertAlmostEqual(rewards_stats['monthly_totals_2025'].get('2025-03', 0), 700.00, places=2)
        
        print(f"✅ Monthly totals correct:")
        print(f"   2024-01: ${rewards_stats['monthly_totals_2024'].get('2024-01', 0):.2f}")
        print(f"   2024-09: ${rewards_stats['monthly_totals_2024'].get('2024-09', 0):.2f}")
        print(f"   2025-03: ${rewards_stats['monthly_totals_2025'].get('2025-03', 0):.2f}")
    
    def test_average_payment_calculation(self):
        """Test that the average payment is calculated correctly"""
        rewards_stats = self.process_rewards(self.test_records)
        
        # Calculate expected average
        expected_total = 100.00 + 150.50 + 200.00 + 250.75 + 300.00 + 350.00 + 400.00 + 450.25 + 1500.00 + 550.75 + 600.00 + 650.00 + 700.00
        expected_count = 13
        expected_average = expected_total / expected_count
        
        # Calculate actual average
        actual_average = rewards_stats['total_amount'] / rewards_stats['total_records_with_amount'] if rewards_stats['total_records_with_amount'] > 0 else 0
        
        self.assertAlmostEqual(actual_average, expected_average, places=2)
        print(f"✅ Average payment calculation correct: ${actual_average:.2f}")
    
    def test_field_case_insensitivity(self):
        """Test that the field detection is case-insensitive"""
        # Create records with different case variations
        case_test_records = [
            {"RegDate": "2024-01-15", "amount": 100.00},  # lowercase
            {"RegDate": "2024-02-20", "AMOUNT": 150.50},  # uppercase
            {"RegDate": "2024-03-10", "Amount": 200.00},  # mixed case
            {"RegDate": "2024-04-05", "reward": 250.75},  # lowercase
            {"RegDate": "2024-05-12", "REWARD": 300.00},  # uppercase
            {"RegDate": "2024-06-18", "Reward": 350.00}   # mixed case
        ]
        
        rewards_stats = self.process_rewards(case_test_records)
        
        # Expected total (sum of all amounts)
        expected_total = 100.00 + 150.50 + 200.00 + 250.75 + 300.00 + 350.00
        
        self.assertAlmostEqual(rewards_stats['total_amount'], expected_total, places=2)
        self.assertEqual(rewards_stats['total_records_with_amount'], 6)
        print(f"✅ Case-insensitive field detection working correctly")
        print(f"   Total amount: ${rewards_stats['total_amount']:.2f}")
        print(f"   Records with amount: {rewards_stats['total_records_with_amount']}")
    
    def test_data_type_handling(self):
        """Test that different data types are handled correctly"""
        # Create records with different data types
        type_test_records = [
            {"RegDate": "2024-01-15", "Amount": 100},      # integer
            {"RegDate": "2024-02-20", "Amount": 150.50},   # float
            {"RegDate": "2024-03-10", "Amount": "200"},    # string integer
            {"RegDate": "2024-04-05", "Amount": "250.75"}, # string float
            {"RegDate": "2024-05-12", "Amount": "$300.00"} # string with dollar sign
        ]
        
        rewards_stats = self.process_rewards(type_test_records)
        
        # Expected total (sum of all amounts)
        expected_total = 100.00 + 150.50 + 200.00 + 250.75 + 300.00
        
        self.assertAlmostEqual(rewards_stats['total_amount'], expected_total, places=2)
        self.assertEqual(rewards_stats['total_records_with_amount'], 5)
        print(f"✅ Data type handling working correctly")
        print(f"   Total amount: ${rewards_stats['total_amount']:.2f}")
        print(f"   Records with amount: {rewards_stats['total_records_with_amount']}")
    
    def test_number_format_handling(self):
        """Test that different number formats are handled correctly"""
        # Create records with different number formats
        format_test_records = [
            {"RegDate": "2024-01-15", "Amount": "$100.00"},    # dollar sign
            {"RegDate": "2024-02-20", "Amount": "150.50"},     # decimal
            {"RegDate": "2024-03-10", "Amount": "$1,200.00"},  # comma
            {"RegDate": "2024-04-05", "Amount": " 250.75 "},   # spaces
            {"RegDate": "2024-05-12", "Amount": "$300"}        # no decimal
        ]
        
        rewards_stats = self.process_rewards(format_test_records)
        
        # Expected total (sum of all amounts)
        expected_total = 100.00 + 150.50 + 1200.00 + 250.75 + 300.00
        
        self.assertAlmostEqual(rewards_stats['total_amount'], expected_total, places=2)
        self.assertEqual(rewards_stats['total_records_with_amount'], 5)
        print(f"✅ Number format handling working correctly")
        print(f"   Total amount: ${rewards_stats['total_amount']:.2f}")
        print(f"   Records with amount: {rewards_stats['total_records_with_amount']}")
    
    def test_invalid_value_handling(self):
        """Test that invalid values are handled correctly"""
        # Create records with invalid values
        invalid_test_records = [
            {"RegDate": "2024-01-15", "Amount": "invalid"},  # invalid string
            {"RegDate": "2024-02-20", "Amount": "null"},     # null string
            {"RegDate": "2024-03-10", "Amount": "none"},     # none string
            {"RegDate": "2024-04-05", "Amount": "nan"},      # nan string
            {"RegDate": "2024-05-12", "Amount": "0"},        # zero string
            {"RegDate": "2024-06-18", "Amount": 0},          # zero integer
            {"RegDate": "2024-07-22", "Amount": 0.0},        # zero float
            {"RegDate": "2024-08-30", "Amount": "0.00"},     # zero decimal string
            {"RegDate": "2024-09-14", "Amount": "$0.00"},    # zero with dollar sign
            {"RegDate": "2024-10-05", "Amount": 100.00}      # valid amount (control)
        ]
        
        rewards_stats = self.process_rewards(invalid_test_records)
        
        # Only the last record should be counted
        expected_total = 100.00
        
        self.assertAlmostEqual(rewards_stats['total_amount'], expected_total, places=2)
        self.assertEqual(rewards_stats['total_records_with_amount'], 1)
        print(f"✅ Invalid value handling working correctly")
        print(f"   Total amount: ${rewards_stats['total_amount']:.2f}")
        print(f"   Records with amount: {rewards_stats['total_records_with_amount']}")


def run_tests():
    """Run all unit tests"""
    print("🚀 Starting Rewards Processing Unit Tests")
    print("=" * 50)
    
    # Create a test suite
    suite = unittest.TestSuite()
    suite.addTest(RewardsProcessingUnitTest('test_total_amount_calculation'))
    suite.addTest(RewardsProcessingUnitTest('test_records_with_amount_count'))
    suite.addTest(RewardsProcessingUnitTest('test_yearly_totals'))
    suite.addTest(RewardsProcessingUnitTest('test_monthly_totals'))
    suite.addTest(RewardsProcessingUnitTest('test_average_payment_calculation'))
    suite.addTest(RewardsProcessingUnitTest('test_field_case_insensitivity'))
    suite.addTest(RewardsProcessingUnitTest('test_data_type_handling'))
    suite.addTest(RewardsProcessingUnitTest('test_number_format_handling'))
    suite.addTest(RewardsProcessingUnitTest('test_invalid_value_handling'))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {result.testsRun - len(result.errors) - len(result.failures)}/{result.testsRun}")
    
    return len(result.errors) == 0 and len(result.failures) == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)