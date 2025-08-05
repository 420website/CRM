#!/usr/bin/env python3
"""
FOCUSED SEEDING STATUS TEST
==========================

This test provides a focused check on the current seeding status and data persistence.
"""

import requests
import json
import os
from dotenv import load_dotenv
from pymongo import MongoClient

def check_seeding_status():
    """Check current seeding status"""
    
    # Load environment variables
    load_dotenv('/app/frontend/.env')
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    
    load_dotenv('/app/backend/.env')
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'my420_ca_db')
    
    print("🔍 SEEDING STATUS CHECK")
    print("=" * 50)
    print(f"Backend URL: {backend_url}")
    print(f"MongoDB URL: {mongo_url}")
    print(f"Database: {db_name}")
    print("=" * 50)
    
    # Check database directly
    try:
        client = MongoClient(mongo_url)
        db = client[db_name]
        
        print("\n📊 DIRECT DATABASE COUNTS:")
        clinical_count = db.clinical_templates.count_documents({})
        notes_count = db.notes_templates.count_documents({})
        dispositions_count = db.dispositions.count_documents({})
        referral_sites_count = db.referral_sites.count_documents({})
        
        print(f"   Clinical Templates: {clinical_count}")
        print(f"   Notes Templates: {notes_count}")
        print(f"   Dispositions: {dispositions_count}")
        print(f"   Referral Sites: {referral_sites_count}")
        
        # Check for default vs custom data
        clinical_default = db.clinical_templates.count_documents({"is_default": True})
        notes_default = db.notes_templates.count_documents({"is_default": True})
        dispositions_default = db.dispositions.count_documents({"is_default": True})
        referral_sites_default = db.referral_sites.count_documents({"is_default": True})
        
        print(f"\n📋 DEFAULT DATA COUNTS:")
        print(f"   Clinical Templates (default): {clinical_default}")
        print(f"   Notes Templates (default): {notes_default}")
        print(f"   Dispositions (default): {dispositions_default}")
        print(f"   Referral Sites (default): {referral_sites_default}")
        
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False
    
    # Check API endpoints
    print(f"\n🌐 API ENDPOINT CHECKS:")
    headers = {'Content-Type': 'application/json'}
    
    endpoints = [
        ("Clinical Templates", "/api/clinical-templates"),
        ("Notes Templates", "/api/notes-templates"),
        ("Dispositions", "/api/dispositions"),
        ("Referral Sites", "/api/referral-sites")
    ]
    
    api_working = True
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{backend_url}{endpoint}", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                print(f"   ✅ {name}: {count} items via API")
            else:
                print(f"   ❌ {name}: API returned status {response.status_code}")
                api_working = False
        except Exception as e:
            print(f"   ❌ {name}: API error - {str(e)}")
            api_working = False
    
    # Summary
    print(f"\n📊 SUMMARY:")
    total_data = clinical_count + notes_count + dispositions_count + referral_sites_count
    
    if total_data == 0:
        print("🚨 CRITICAL: NO SEEDED DATA FOUND!")
        print("   This confirms the user's report of data loss.")
        return False
    elif clinical_count == 0 or notes_count == 0 or dispositions_count == 0 or referral_sites_count == 0:
        print("⚠️  WARNING: Some collections are empty!")
        print("   Partial seeding failure detected.")
        return False
    else:
        print("✅ All seeded data collections have data.")
        print("   Seeding appears to be working correctly.")
        
        if api_working:
            print("✅ All API endpoints are working.")
        else:
            print("⚠️  Some API endpoints have issues.")
            
        return True

if __name__ == "__main__":
    success = check_seeding_status()
    exit(0 if success else 1)