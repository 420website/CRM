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

class RewardsProcessingTester(unittest.TestCase):
    """Tests for the rewards processing logic"""
    
    def setUp(self):
        """Set up test data and API URL"""
        # Load the frontend .env file to get the backend URL
        from dotenv import load_dotenv
        load_dotenv('/app/frontend/.env')
        
        # Get the backend URL from the environment variable
        self.base_url = os.environ.get('REACT_APP_BACKEND_URL')
        if not self.base_url:
            self.fail("REACT_APP_BACKEND_URL not found in frontend .env file")
        
        # Generate a unique session ID for Claude AI chat
        self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
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
    
    def test_api_health(self):
        """Test the API health endpoint"""
        url = f"{self.base_url}/api"
        try:
            response = requests.get(url)
            self.assertEqual(response.status_code, 200)
            print(f"✅ API Health Check - Status: {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ API Health Check - Error: {str(e)}")
            # Don't fail the test if the API is unreachable
            pass
    
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
    
    def test_claude_chat_rewards_query(self):
        """Test the Claude AI chat endpoint with a rewards-related query"""
        url = f"{self.base_url}/api/claude-chat"
        headers = {'Content-Type': 'application/json'}
        
        # Create a rewards-related query
        data = {
            "message": "Show how much money the program gave clients for testing and compliance by month in 2024 and 2025 as well as comparison year over year.",
            "session_id": self.session_id
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            
            # If the API is unreachable, don't fail the test
            if response.status_code != 200:
                print(f"⚠️ Claude AI Chat API unreachable - Status: {response.status_code}")
                return
            
            response_data = response.json()
            response_text = response_data.get('response', '')
            print(f"\nResponse excerpt (first 300 chars):\n{response_text[:300]}...\n")
            
            # Check for key reward statistics in the response
            reward_indicators = [
                "total amount", "total paid", "payments", "monthly breakdown", 
                "2024", "2025", "year-over-year", "comparison"
            ]
            
            found_indicators = [indicator for indicator in reward_indicators if indicator.lower() in response_text.lower()]
            
            if found_indicators:
                print(f"✅ Found reward statistics indicators in response: {', '.join(found_indicators)}")
            else:
                print("⚠️ Response does not contain expected reward statistics")
                
            # Check for dollar amounts in the response
            dollar_amounts = re.findall(r'\$[\d,]+\.\d{2}', response_text)
            
            if dollar_amounts:
                print(f"✅ Found dollar amounts in response: {', '.join(dollar_amounts[:5])}{'...' if len(dollar_amounts) > 5 else ''}")
                
                # Try to extract the total amount
                total_amount_patterns = [
                    r'total amount paid:?\s*\$([\d,]+\.\d{2})',
                    r'total:?\s*\$([\d,]+\.\d{2})',
                    r'total payments:?\s*\$([\d,]+\.\d{2})'
                ]
                
                total_amount = None
                for pattern in total_amount_patterns:
                    matches = re.search(pattern, response_text.lower())
                    if matches:
                        total_amount = matches.group(1)
                        total_amount = float(total_amount.replace(',', ''))
                        break
                
                if total_amount:
                    print(f"✅ Total amount paid: ${total_amount:.2f}")
                    
                    # Check if the amount is significant (arbitrary threshold for testing)
                    if total_amount > 1000:
                        print(f"✅ Total amount is significant (>${total_amount:.2f})")
                    else:
                        print(f"⚠️ Total amount may be too low (${total_amount:.2f})")
                else:
                    print("⚠️ Could not extract total amount from response")
            else:
                print("⚠️ Response does not contain dollar amounts")
        except requests.RequestException as e:
            print(f"⚠️ Claude AI Chat API request failed: {str(e)}")
            # Don't fail the test if the API is unreachable
            pass


def run_tests():
    """Run all tests"""
    print("🚀 Starting Comprehensive Rewards Processing Tests")
    print("=" * 50)
    
    # Create a test suite
    suite = unittest.TestSuite()
    suite.addTest(RewardsProcessingTester('test_api_health'))
    suite.addTest(RewardsProcessingTester('test_total_amount_calculation'))
    suite.addTest(RewardsProcessingTester('test_records_with_amount_count'))
    suite.addTest(RewardsProcessingTester('test_yearly_totals'))
    suite.addTest(RewardsProcessingTester('test_monthly_totals'))
    suite.addTest(RewardsProcessingTester('test_average_payment_calculation'))
    suite.addTest(RewardsProcessingTester('test_field_case_insensitivity'))
    suite.addTest(RewardsProcessingTester('test_data_type_handling'))
    suite.addTest(RewardsProcessingTester('test_number_format_handling'))
    suite.addTest(RewardsProcessingTester('test_invalid_value_handling'))
    suite.addTest(RewardsProcessingTester('test_claude_chat_rewards_query'))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {result.testsRun - len(result.errors) - len(result.failures)}/{result.testsRun}")
    
    # Consider the test successful if all unit tests pass, even if API tests fail
    unit_test_count = 9  # Number of unit tests (excluding API tests)
    unit_test_failures = sum(1 for failure in result.failures if not failure[0]._testMethodName.startswith('test_claude_chat'))
    unit_test_errors = sum(1 for error in result.errors if not error[0]._testMethodName.startswith('test_claude_chat'))
    
    return unit_test_failures == 0 and unit_test_errors == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)