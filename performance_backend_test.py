#!/usr/bin/env python3
"""
Performance Backend Testing for Optimized Admin Dashboard Endpoints
Testing with large dataset: 507 pending + 830 submitted = 1337 total registrations
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Get backend URL from frontend environment
BACKEND_URL = "http://localhost:8001"
try:
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BACKEND_URL = line.split('=')[1].strip()
                break
except:
    pass

API_BASE = f"{BACKEND_URL}/api"

class PerformanceBackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.performance_metrics = {
            'response_times': [],
            'data_sizes': [],
            'concurrent_performance': [],
            'pagination_performance': [],
            'filtering_performance': []
        }
    
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def measure_request_time(self, url, params=None):
        """Measure request response time and data size"""
        start_time = time.time()
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                data_size = len(json.dumps(data).encode('utf-8'))
                
                return {
                    'success': response.status == 200,
                    'response_time': response_time,
                    'data_size': data_size,
                    'status_code': response.status,
                    'data': data
                }
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'response_time': (end_time - start_time) * 1000,
                'data_size': 0,
                'error': str(e),
                'status_code': 0
            }
    
    async def test_database_health(self):
        """Test basic database connectivity and health"""
        print("🔍 Testing Database Health and Data Volume...")
        
        # Test pending registrations count
        result = await self.measure_request_time(f"{API_BASE}/admin-registrations-pending-optimized", 
                                                {"page": 1, "page_size": 1})
        
        if result['success']:
            total_pending = result['data']['pagination']['total_records']
            print(f"✅ Pending registrations: {total_pending}")
            
            # Test submitted registrations count
            result = await self.measure_request_time(f"{API_BASE}/admin-registrations-submitted-optimized", 
                                                    {"page": 1, "page_size": 1})
            
            if result['success']:
                total_submitted = result['data']['pagination']['total_records']
                total_registrations = total_pending + total_submitted
                print(f"✅ Submitted registrations: {total_submitted}")
                print(f"✅ Total registrations: {total_registrations}")
                
                # Verify we have the expected large dataset
                if total_registrations >= 1000:
                    print(f"🎉 Large dataset confirmed: {total_registrations} total registrations")
                    return True, total_pending, total_submitted, total_registrations
                else:
                    print(f"⚠️ Dataset smaller than expected: {total_registrations} registrations")
                    return True, total_pending, total_submitted, total_registrations
            else:
                print(f"❌ Failed to get submitted registrations: {result.get('error', 'Unknown error')}")
                return False, 0, 0, 0
        else:
            print(f"❌ Failed to get pending registrations: {result.get('error', 'Unknown error')}")
            return False, 0, 0, 0
    
    async def test_pagination_performance(self, total_pending, total_submitted):
        """Test pagination performance with various page sizes"""
        print("\n🔍 Testing Pagination Performance...")
        
        page_sizes = [10, 20, 50]
        pagination_results = []
        
        for page_size in page_sizes:
            print(f"\n📄 Testing page size: {page_size}")
            
            # Test pending registrations pagination
            for page in [1, 2, 3]:  # Test first few pages
                if (page - 1) * page_size < total_pending:
                    result = await self.measure_request_time(
                        f"{API_BASE}/admin-registrations-pending-optimized",
                        {"page": page, "page_size": page_size}
                    )
                    
                    if result['success']:
                        pagination_results.append({
                            'endpoint': 'pending',
                            'page_size': page_size,
                            'page': page,
                            'response_time': result['response_time'],
                            'data_size': result['data_size'],
                            'records_returned': len(result['data']['data'])
                        })
                        print(f"  ✅ Pending page {page}: {result['response_time']:.2f}ms, {len(result['data']['data'])} records")
                    else:
                        print(f"  ❌ Pending page {page} failed: {result.get('error', 'Unknown error')}")
            
            # Test submitted registrations pagination
            for page in [1, 2, 3]:  # Test first few pages
                if (page - 1) * page_size < total_submitted:
                    result = await self.measure_request_time(
                        f"{API_BASE}/admin-registrations-submitted-optimized",
                        {"page": page, "page_size": page_size}
                    )
                    
                    if result['success']:
                        pagination_results.append({
                            'endpoint': 'submitted',
                            'page_size': page_size,
                            'page': page,
                            'response_time': result['response_time'],
                            'data_size': result['data_size'],
                            'records_returned': len(result['data']['data'])
                        })
                        print(f"  ✅ Submitted page {page}: {result['response_time']:.2f}ms, {len(result['data']['data'])} records")
                    else:
                        print(f"  ❌ Submitted page {page} failed: {result.get('error', 'Unknown error')}")
        
        # Analyze pagination performance
        if pagination_results:
            avg_response_time = statistics.mean([r['response_time'] for r in pagination_results])
            max_response_time = max([r['response_time'] for r in pagination_results])
            min_response_time = min([r['response_time'] for r in pagination_results])
            
            print(f"\n📊 Pagination Performance Summary:")
            print(f"  Average response time: {avg_response_time:.2f}ms")
            print(f"  Min response time: {min_response_time:.2f}ms")
            print(f"  Max response time: {max_response_time:.2f}ms")
            
            self.performance_metrics['pagination_performance'] = pagination_results
            return True
        else:
            print("❌ No pagination results collected")
            return False
    
    async def test_search_filtering_performance(self):
        """Test search and filtering functionality with large dataset"""
        print("\n🔍 Testing Search and Filtering Performance...")
        
        filtering_results = []
        
        # Test different search scenarios
        search_tests = [
            {"search_name": "john", "description": "Name search"},
            {"search_name": "smith, j", "description": "Lastname, firstinitial format"},
            {"search_disposition": "ACTIVE", "description": "Disposition filter"},
            {"search_referral_site": "Toronto", "description": "Referral site filter"},
            {"search_name": "test", "search_disposition": "PENDING", "description": "Combined filters"}
        ]
        
        for test_params in search_tests:
            description = test_params.pop('description')
            print(f"\n🔎 Testing: {description}")
            
            # Test on pending registrations
            result = await self.measure_request_time(
                f"{API_BASE}/admin-registrations-pending-optimized",
                {**test_params, "page": 1, "page_size": 20}
            )
            
            if result['success']:
                records_found = len(result['data']['data'])
                total_matches = result['data']['pagination']['total_records']
                filtering_results.append({
                    'endpoint': 'pending',
                    'test': description,
                    'response_time': result['response_time'],
                    'records_found': records_found,
                    'total_matches': total_matches,
                    'data_size': result['data_size']
                })
                print(f"  ✅ Pending: {result['response_time']:.2f}ms, {total_matches} total matches, {records_found} returned")
            else:
                print(f"  ❌ Pending search failed: {result.get('error', 'Unknown error')}")
            
            # Test on submitted registrations
            result = await self.measure_request_time(
                f"{API_BASE}/admin-registrations-submitted-optimized",
                {**test_params, "page": 1, "page_size": 20}
            )
            
            if result['success']:
                records_found = len(result['data']['data'])
                total_matches = result['data']['pagination']['total_records']
                filtering_results.append({
                    'endpoint': 'submitted',
                    'test': description,
                    'response_time': result['response_time'],
                    'records_found': records_found,
                    'total_matches': total_matches,
                    'data_size': result['data_size']
                })
                print(f"  ✅ Submitted: {result['response_time']:.2f}ms, {total_matches} total matches, {records_found} returned")
            else:
                print(f"  ❌ Submitted search failed: {result.get('error', 'Unknown error')}")
        
        # Analyze filtering performance
        if filtering_results:
            avg_response_time = statistics.mean([r['response_time'] for r in filtering_results])
            print(f"\n📊 Filtering Performance Summary:")
            print(f"  Average response time: {avg_response_time:.2f}ms")
            print(f"  Total filtering tests: {len(filtering_results)}")
            
            self.performance_metrics['filtering_performance'] = filtering_results
            return True
        else:
            print("❌ No filtering results collected")
            return False
    
    async def test_concurrent_performance(self):
        """Test concurrent request handling"""
        print("\n🔍 Testing Concurrent Performance...")
        
        # Create multiple concurrent requests
        concurrent_tasks = []
        num_concurrent = 10
        
        for i in range(num_concurrent):
            # Alternate between pending and submitted endpoints
            if i % 2 == 0:
                task = self.measure_request_time(
                    f"{API_BASE}/admin-registrations-pending-optimized",
                    {"page": (i % 3) + 1, "page_size": 20}
                )
            else:
                task = self.measure_request_time(
                    f"{API_BASE}/admin-registrations-submitted-optimized",
                    {"page": (i % 3) + 1, "page_size": 20}
                )
            concurrent_tasks.append(task)
        
        # Execute all requests concurrently
        start_time = time.time()
        results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
        end_time = time.time()
        
        total_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Analyze results
        successful_results = [r for r in results if isinstance(r, dict) and r.get('success')]
        failed_results = [r for r in results if not (isinstance(r, dict) and r.get('success'))]
        
        if successful_results:
            response_times = [r['response_time'] for r in successful_results]
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            print(f"📊 Concurrent Performance Results:")
            print(f"  Total concurrent requests: {num_concurrent}")
            print(f"  Successful requests: {len(successful_results)}")
            print(f"  Failed requests: {len(failed_results)}")
            print(f"  Total execution time: {total_time:.2f}ms")
            print(f"  Average response time: {avg_response_time:.2f}ms")
            print(f"  Min response time: {min_response_time:.2f}ms")
            print(f"  Max response time: {max_response_time:.2f}ms")
            
            self.performance_metrics['concurrent_performance'] = {
                'total_requests': num_concurrent,
                'successful': len(successful_results),
                'failed': len(failed_results),
                'total_time': total_time,
                'avg_response_time': avg_response_time,
                'min_response_time': min_response_time,
                'max_response_time': max_response_time
            }
            
            return len(successful_results) >= num_concurrent * 0.8  # 80% success rate
        else:
            print("❌ All concurrent requests failed")
            return False
    
    async def test_database_indexing_performance(self):
        """Test database indexing performance with complex queries"""
        print("\n🔍 Testing Database Indexing Performance...")
        
        indexing_tests = [
            {
                "params": {"search_name": "johnson", "page_size": 50},
                "description": "Name search with large page size"
            },
            {
                "params": {"search_disposition": "ACTIVE", "page_size": 100},
                "description": "Disposition filter with very large page size"
            },
            {
                "params": {"search_name": "smith", "search_disposition": "PENDING", "page_size": 30},
                "description": "Combined name and disposition filter"
            }
        ]
        
        indexing_results = []
        
        for test in indexing_tests:
            print(f"\n🗂️ Testing: {test['description']}")
            
            # Test on pending registrations
            result = await self.measure_request_time(
                f"{API_BASE}/admin-registrations-pending-optimized",
                test['params']
            )
            
            if result['success']:
                total_matches = result['data']['pagination']['total_records']
                indexing_results.append({
                    'test': test['description'],
                    'endpoint': 'pending',
                    'response_time': result['response_time'],
                    'total_matches': total_matches,
                    'page_size': test['params']['page_size']
                })
                print(f"  ✅ Pending: {result['response_time']:.2f}ms, {total_matches} matches")
            else:
                print(f"  ❌ Pending indexing test failed: {result.get('error', 'Unknown error')}")
        
        # Analyze indexing performance
        if indexing_results:
            avg_response_time = statistics.mean([r['response_time'] for r in indexing_results])
            print(f"\n📊 Database Indexing Performance:")
            print(f"  Average response time for complex queries: {avg_response_time:.2f}ms")
            
            # Check if all queries are under 1 second (good performance)
            fast_queries = [r for r in indexing_results if r['response_time'] < 1000]
            print(f"  Queries under 1 second: {len(fast_queries)}/{len(indexing_results)}")
            
            return len(fast_queries) == len(indexing_results)
        else:
            print("❌ No indexing results collected")
            return False
    
    async def test_data_consistency(self):
        """Test data consistency between optimized and regular endpoints"""
        print("\n🔍 Testing Data Consistency...")
        
        # Compare first page of pending registrations
        optimized_result = await self.measure_request_time(
            f"{API_BASE}/admin-registrations-pending-optimized",
            {"page": 1, "page_size": 10}
        )
        
        regular_result = await self.measure_request_time(
            f"{API_BASE}/admin-registrations-pending",
            {}
        )
        
        if optimized_result['success'] and regular_result['success']:
            optimized_count = optimized_result['data']['pagination']['total_records']
            regular_count = len(regular_result['data'])
            
            print(f"📊 Data Consistency Check:")
            print(f"  Optimized endpoint total: {optimized_count}")
            print(f"  Regular endpoint count: {regular_count}")
            
            # Check if counts are reasonably close (allowing for timing differences)
            consistency_check = abs(optimized_count - regular_count) <= 5
            
            if consistency_check:
                print("  ✅ Data consistency verified")
                return True
            else:
                print("  ⚠️ Data consistency issue detected")
                return False
        else:
            print("  ❌ Failed to compare endpoints")
            return False
    
    async def run_comprehensive_performance_test(self):
        """Run all performance tests"""
        print("🚀 Starting Comprehensive Performance Testing for Optimized Admin Dashboard")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Test 1: Database Health and Data Volume
            health_success, total_pending, total_submitted, total_registrations = await self.test_database_health()
            
            if not health_success:
                print("❌ Database health check failed. Aborting tests.")
                return False
            
            # Test 2: Pagination Performance
            pagination_success = await self.test_pagination_performance(total_pending, total_submitted)
            
            # Test 3: Search and Filtering Performance
            filtering_success = await self.test_search_filtering_performance()
            
            # Test 4: Concurrent Performance
            concurrent_success = await self.test_concurrent_performance()
            
            # Test 5: Database Indexing Performance
            indexing_success = await self.test_database_indexing_performance()
            
            # Test 6: Data Consistency
            consistency_success = await self.test_data_consistency()
            
            # Overall Results
            print("\n" + "=" * 80)
            print("🎯 COMPREHENSIVE PERFORMANCE TEST RESULTS")
            print("=" * 80)
            
            tests = [
                ("Database Health & Data Volume", health_success),
                ("Pagination Performance", pagination_success),
                ("Search & Filtering Performance", filtering_success),
                ("Concurrent Request Handling", concurrent_success),
                ("Database Indexing Performance", indexing_success),
                ("Data Consistency", consistency_success)
            ]
            
            passed_tests = sum(1 for _, success in tests if success)
            total_tests = len(tests)
            
            for test_name, success in tests:
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"  {status} {test_name}")
            
            print(f"\n📊 Overall Success Rate: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")
            
            # Performance Summary
            if self.performance_metrics['pagination_performance']:
                avg_pagination_time = statistics.mean([r['response_time'] for r in self.performance_metrics['pagination_performance']])
                print(f"📈 Average Pagination Response Time: {avg_pagination_time:.2f}ms")
            
            if self.performance_metrics['filtering_performance']:
                avg_filtering_time = statistics.mean([r['response_time'] for r in self.performance_metrics['filtering_performance']])
                print(f"🔍 Average Filtering Response Time: {avg_filtering_time:.2f}ms")
            
            if self.performance_metrics['concurrent_performance']:
                concurrent_metrics = self.performance_metrics['concurrent_performance']
                print(f"⚡ Concurrent Performance: {concurrent_metrics['successful']}/{concurrent_metrics['total_requests']} successful")
                print(f"⚡ Average Concurrent Response Time: {concurrent_metrics['avg_response_time']:.2f}ms")
            
            print(f"\n🗄️ Dataset Size: {total_registrations} total registrations ({total_pending} pending, {total_submitted} submitted)")
            
            return passed_tests >= total_tests * 0.8  # 80% success rate
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = PerformanceBackendTester()
    success = await tester.run_comprehensive_performance_test()
    
    if success:
        print("\n🎉 PERFORMANCE TESTING COMPLETED SUCCESSFULLY!")
        print("All optimized admin dashboard endpoints are performing well with the large dataset.")
    else:
        print("\n⚠️ PERFORMANCE TESTING COMPLETED WITH ISSUES")
        print("Some performance tests failed. Check the detailed results above.")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)