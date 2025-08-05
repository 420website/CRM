#!/usr/bin/env python3
"""
URGENT DATA INTEGRITY INVESTIGATION
===================================
Investigating critical data loss issue where 60+ submitted clients disappeared after redeployment.
"""

import requests
import json
import os
from datetime import datetime
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Get backend URL from frontend env
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.split('=')[1].strip()
            break

API_BASE = f"{BACKEND_URL}/api"

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'my420_ca_db')

print("🚨 URGENT: DATA INTEGRITY INVESTIGATION STARTING")
print("=" * 60)
print(f"Backend URL: {BACKEND_URL}")
print(f"API Base: {API_BASE}")
print(f"MongoDB URL: {MONGO_URL}")
print(f"Database: {DB_NAME}")
print("=" * 60)

async def investigate_database_directly():
    """Direct database investigation"""
    print("\n🔍 DIRECT DATABASE INVESTIGATION")
    print("-" * 40)
    
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # 1. Total count of all registrations
        total_count = await db.admin_registrations.count_documents({})
        print(f"📊 Total registrations in database: {total_count}")
        
        # 2. Count by status
        print("\n📈 Registration counts by status:")
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        status_counts = await db.admin_registrations.aggregate(pipeline).to_list(length=None)
        
        for status_doc in status_counts:
            status = status_doc['_id'] or 'NULL'
            count = status_doc['count']
            print(f"  • {status}: {count}")
        
        # 3. List all unique status values
        unique_statuses = await db.admin_registrations.distinct("status")
        print(f"\n🏷️ All unique status values: {unique_statuses}")
        
        # 4. Check for finalized_at timestamps (submitted clients should have these)
        finalized_count = await db.admin_registrations.count_documents({"finalized_at": {"$exists": True, "$ne": None}})
        print(f"\n⏰ Registrations with finalized_at timestamp: {finalized_count}")
        
        # 5. Sample registrations analysis
        print("\n🔬 SAMPLE REGISTRATIONS ANALYSIS:")
        print("-" * 30)
        
        # Get 5 most recent registrations
        recent_registrations = await db.admin_registrations.find({}).sort("timestamp", -1).limit(5).to_list(length=5)
        
        for i, reg in enumerate(recent_registrations, 1):
            print(f"\nSample {i}:")
            print(f"  ID: {reg.get('id', 'N/A')}")
            print(f"  Name: {reg.get('firstName', 'N/A')} {reg.get('lastName', 'N/A')}")
            print(f"  Status: {reg.get('status', 'N/A')}")
            print(f"  Timestamp: {reg.get('timestamp', 'N/A')}")
            print(f"  Finalized At: {reg.get('finalized_at', 'N/A')}")
            print(f"  Registration Date: {reg.get('regDate', 'N/A')}")
        
        # 6. Check for any registrations that might have been submitted
        completed_registrations = await db.admin_registrations.find({"status": "completed"}).limit(10).to_list(length=10)
        print(f"\n✅ Found {len(completed_registrations)} registrations with 'completed' status")
        
        if completed_registrations:
            print("Sample completed registrations:")
            for reg in completed_registrations[:3]:
                print(f"  • {reg.get('firstName', 'N/A')} {reg.get('lastName', 'N/A')} - {reg.get('finalized_at', 'No finalized_at')}")
        
        # 7. Check for registrations with finalized_at but different status
        finalized_but_not_completed = await db.admin_registrations.find({
            "finalized_at": {"$exists": True, "$ne": None},
            "status": {"$ne": "completed"}
        }).limit(10).to_list(length=10)
        
        print(f"\n⚠️ Registrations with finalized_at but not 'completed' status: {len(finalized_but_not_completed)}")
        if finalized_but_not_completed:
            for reg in finalized_but_not_completed[:3]:
                print(f"  • {reg.get('firstName', 'N/A')} {reg.get('lastName', 'N/A')} - Status: {reg.get('status', 'N/A')}, Finalized: {reg.get('finalized_at', 'N/A')}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Database investigation failed: {str(e)}")

def test_backend_endpoints():
    """Test backend endpoints for submitted registrations"""
    print("\n🌐 BACKEND ENDPOINTS TESTING")
    print("-" * 40)
    
    try:
        # Test health check
        response = requests.get(f"{API_BASE}/health", timeout=10)
        print(f"🏥 Backend health: {response.status_code}")
        
        # Test admin-registrations-submitted-optimized endpoint
        print("\n📋 Testing optimized submitted endpoint:")
        response = requests.get(f"{API_BASE}/admin-registrations-submitted-optimized", timeout=10)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Total submitted (optimized): {data.get('total', 'N/A')}")
            print(f"  Results count: {len(data.get('results', []))}")
            
            if data.get('results'):
                print("  Sample submitted registrations:")
                for reg in data['results'][:3]:
                    print(f"    • {reg.get('firstName', 'N/A')} {reg.get('lastName', 'N/A')} - {reg.get('status', 'N/A')}")
        else:
            print(f"  Error: {response.text}")
        
        # Test regular admin-registrations-submitted endpoint
        print("\n📋 Testing regular submitted endpoint:")
        response = requests.get(f"{API_BASE}/admin-registrations-submitted", timeout=10)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Submitted registrations count: {len(data)}")
            
            if data:
                print("  Sample submitted registrations:")
                for reg in data[:3]:
                    print(f"    • {reg.get('firstName', 'N/A')} {reg.get('lastName', 'N/A')} - {reg.get('status', 'N/A')}")
        else:
            print(f"  Error: {response.text}")
        
        # Test dashboard stats endpoint
        print("\n📊 Testing dashboard stats endpoint:")
        response = requests.get(f"{API_BASE}/admin-dashboard-stats", timeout=10)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"  Pending registrations: {stats.get('pending_registrations', 'N/A')}")
            print(f"  Submitted registrations: {stats.get('submitted_registrations', 'N/A')}")
            print(f"  Total registrations: {stats.get('total_registrations', 'N/A')}")
        else:
            print(f"  Error: {response.text}")
        
        # Test pending registrations for comparison
        print("\n📋 Testing pending registrations:")
        response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized", timeout=10)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Total pending (optimized): {data.get('total', 'N/A')}")
            print(f"  Results count: {len(data.get('results', []))}")
        else:
            print(f"  Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Backend endpoint testing failed: {str(e)}")

def check_backup_files():
    """Check for backup files that might contain missing data"""
    print("\n💾 BACKUP FILES INVESTIGATION")
    print("-" * 40)
    
    backup_paths = [
        '/app/persistent-data/client-backups/',
        '/app/persistent-data/backups/',
        '/app/persistent-data/'
    ]
    
    for backup_path in backup_paths:
        print(f"\n📁 Checking {backup_path}:")
        
        if os.path.exists(backup_path):
            try:
                files = os.listdir(backup_path)
                if files:
                    print(f"  Found {len(files)} files:")
                    for file in sorted(files):
                        file_path = os.path.join(backup_path, file)
                        if os.path.isfile(file_path):
                            size = os.path.getsize(file_path)
                            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                            print(f"    • {file} ({size} bytes, modified: {mtime})")
                            
                            # Check if it's a JSON backup file with registration data
                            if file.endswith('.json') and 'registration' in file.lower():
                                try:
                                    with open(file_path, 'r') as f:
                                        data = json.load(f)
                                        if isinstance(data, list):
                                            print(f"      → Contains {len(data)} records")
                                            
                                            # Check for submitted/completed records
                                            completed_count = sum(1 for record in data if record.get('status') == 'completed')
                                            finalized_count = sum(1 for record in data if record.get('finalized_at'))
                                            
                                            if completed_count > 0:
                                                print(f"      → {completed_count} completed records found!")
                                            if finalized_count > 0:
                                                print(f"      → {finalized_count} finalized records found!")
                                                
                                except Exception as e:
                                    print(f"      → Error reading JSON: {str(e)}")
                else:
                    print("  Directory is empty")
            except Exception as e:
                print(f"  Error accessing directory: {str(e)}")
        else:
            print("  Directory does not exist")

async def main():
    """Main investigation function"""
    print("🚨 STARTING COMPREHENSIVE DATA INTEGRITY INVESTIGATION")
    print("This investigation will check for the missing 60+ submitted clients")
    print()
    
    # 1. Direct database investigation
    await investigate_database_directly()
    
    # 2. Backend endpoints testing
    test_backend_endpoints()
    
    # 3. Backup files investigation
    check_backup_files()
    
    print("\n" + "=" * 60)
    print("🔍 DATA INTEGRITY INVESTIGATION COMPLETED")
    print("=" * 60)
    print("\nSUMMARY:")
    print("- Database counts and status analysis completed")
    print("- Backend endpoint functionality tested")
    print("- Backup files investigated for missing data")
    print("\nPlease review the results above to identify the root cause")
    print("of the missing submitted clients issue.")

if __name__ == "__main__":
    asyncio.run(main())