import requests
import json
import time
from datetime import datetime, timedelta
import base64
import uuid
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend .env
backend_url = os.environ.get('REACT_APP_BACKEND_URL')
if not backend_url:
    print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
    exit(1)

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME')
client = MongoClient(mongo_url)
db = client[db_name]

print(f"🔍 Debugging Sharing Functionality")
print(f"🔗 Backend URL: {backend_url}")
print(f"🔗 MongoDB URL: {mongo_url}")
print(f"🔗 Database: {db_name}")
print("=" * 50)

def generate_sample_base64_image():
    """Generate a simple base64 encoded image for testing"""
    # This is a tiny 1x1 pixel transparent PNG image encoded as base64
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

def check_ttl_index():
    """Check if TTL index exists on temporary_shares collection"""
    print("\n🔍 Checking TTL index on temporary_shares collection...")
    
    try:
        # Get collection info
        indexes = list(db.temporary_shares.list_indexes())
        ttl_index_found = False
        
        for index in indexes:
            if 'expireAfterSeconds' in index and 'expires_at' in index['key']:
                ttl_index_found = True
                print(f"✅ TTL index found: {index}")
                print(f"✅ expireAfterSeconds: {index['expireAfterSeconds']}")
                break
        
        if not ttl_index_found:
            print("❌ No TTL index found on temporary_shares collection")
            
            # Create TTL index
            print("🔧 Creating TTL index...")
            result = db.temporary_shares.create_index("expires_at", expireAfterSeconds=0)
            print(f"✅ TTL index created: {result}")
            
        return ttl_index_found
    except Exception as e:
        print(f"❌ Error checking TTL index: {str(e)}")
        return False

def check_collection_contents():
    """Check contents of temporary_shares collection"""
    print("\n🔍 Checking contents of temporary_shares collection...")
    
    try:
        count = db.temporary_shares.count_documents({})
        print(f"📊 Found {count} documents in temporary_shares collection")
        
        if count > 0:
            # Get the most recent documents
            recent_shares = list(db.temporary_shares.find().sort("created_at", -1).limit(5))
            print(f"📊 Most recent {len(recent_shares)} shares:")
            
            for share in recent_shares:
                created_at = share.get("created_at", "Unknown")
                expires_at = share.get("expires_at", "Unknown")
                access_count = share.get("access_count", 0)
                
                # Calculate time until expiration
                if isinstance(expires_at, datetime):
                    now = datetime.utcnow()
                    if expires_at > now:
                        time_left = expires_at - now
                        time_left_str = f"{time_left.total_seconds()/60:.1f} minutes"
                    else:
                        time_left_str = "EXPIRED"
                else:
                    time_left_str = "Unknown"
                
                print(f"  - ID: {share.get('id', 'Unknown')}")
                print(f"    Created: {created_at}")
                print(f"    Expires: {expires_at} (Time left: {time_left_str})")
                print(f"    Access count: {access_count}")
                print(f"    Has attachment data: {'Yes' if 'attachment_data' in share else 'No'}")
                print("    " + "-" * 40)
        
        return count
    except Exception as e:
        print(f"❌ Error checking collection contents: {str(e)}")
        return 0

def create_test_share():
    """Create a test share and return the response"""
    print("\n🔍 Creating test share...")
    
    try:
        # Create attachment data
        attachment_data = {
            "url": generate_sample_base64_image(),
            "filename": f"test_image_{uuid.uuid4()}.png",
            "type": "Image",
            "description": "Test image for debugging"
        }
        
        # Create share request
        share_request = {
            "attachment_data": attachment_data,
            "expires_in_minutes": 30
        }
        
        # Send request to create share
        response = requests.post(
            f"{backend_url}/api/share-attachment",
            json=share_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            share_data = response.json()
            print(f"✅ Share created successfully")
            print(f"  - Share ID: {share_data.get('share_id', 'Unknown')}")
            print(f"  - Share URL: {share_data.get('share_url', 'Unknown')}")
            print(f"  - Preview URL: {share_data.get('preview_url', 'Unknown')}")
            print(f"  - Expires at: {share_data.get('expires_at', 'Unknown')}")
            print(f"  - Expires in: {share_data.get('expires_in_minutes', 'Unknown')} minutes")
            return share_data
        else:
            print(f"❌ Failed to create share: {response.status_code}")
            try:
                error_data = response.json()
                print(f"  - Error: {error_data}")
            except:
                print(f"  - Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating test share: {str(e)}")
        return None

def test_share_access(share_data):
    """Test accessing a shared attachment"""
    if not share_data:
        print("❌ No share data provided")
        return False
    
    share_id = share_data.get("share_id")
    preview_url = share_data.get("preview_url")
    share_url = share_data.get("share_url")
    
    if not share_id or not preview_url or not share_url:
        print("❌ Invalid share data")
        return False
    
    print(f"\n🔍 Testing access to shared attachment (ID: {share_id})...")
    
    # Test preview URL
    print(f"🔍 Testing preview URL: {preview_url}")
    try:
        preview_response = requests.get(preview_url)
        if preview_response.status_code == 200:
            content_type = preview_response.headers.get("Content-Type", "Unknown")
            content_length = len(preview_response.content)
            print(f"✅ Preview access successful")
            print(f"  - Content-Type: {content_type}")
            print(f"  - Content-Length: {content_length} bytes")
        else:
            print(f"❌ Preview access failed: {preview_response.status_code}")
            try:
                error_data = preview_response.json()
                print(f"  - Error: {error_data}")
            except:
                print(f"  - Response: {preview_response.text}")
            return False
    except Exception as e:
        print(f"❌ Error accessing preview URL: {str(e)}")
        return False
    
    # Test download URL
    print(f"🔍 Testing download URL: {share_url}")
    try:
        download_response = requests.get(share_url)
        if download_response.status_code == 200:
            content_type = download_response.headers.get("Content-Type", "Unknown")
            content_length = len(download_response.content)
            print(f"✅ Download access successful")
            print(f"  - Content-Type: {content_type}")
            print(f"  - Content-Length: {content_length} bytes")
        else:
            print(f"❌ Download access failed: {download_response.status_code}")
            try:
                error_data = download_response.json()
                print(f"  - Error: {error_data}")
            except:
                print(f"  - Response: {download_response.text}")
            return False
    except Exception as e:
        print(f"❌ Error accessing download URL: {str(e)}")
        return False
    
    return True

def verify_mongodb_document(share_id):
    """Verify that the share document exists in MongoDB"""
    print(f"\n🔍 Verifying MongoDB document for share ID: {share_id}...")
    
    try:
        # Find the document
        share_doc = db.temporary_shares.find_one({"id": share_id})
        
        if share_doc:
            print(f"✅ Document found in MongoDB")
            
            # Check fields
            created_at = share_doc.get("created_at")
            expires_at = share_doc.get("expires_at")
            access_count = share_doc.get("access_count", 0)
            attachment_data = share_doc.get("attachment_data")
            
            print(f"  - Created at: {created_at}")
            print(f"  - Expires at: {expires_at}")
            print(f"  - Access count: {access_count}")
            print(f"  - Has attachment data: {'Yes' if attachment_data else 'No'}")
            
            # Check if expiration is in the future
            if expires_at:
                now = datetime.utcnow()
                if expires_at > now:
                    time_left = expires_at - now
                    print(f"  - Time until expiration: {time_left.total_seconds()/60:.1f} minutes")
                else:
                    print(f"❌ Document has expired: {expires_at} < {now}")
                    return False
            
            return True
        else:
            print(f"❌ Document not found in MongoDB")
            return False
    except Exception as e:
        print(f"❌ Error verifying MongoDB document: {str(e)}")
        return False

def test_expired_share():
    """Test creating a share with a very short expiration time"""
    print("\n🔍 Testing share expiration...")
    
    try:
        # Create attachment data
        attachment_data = {
            "url": generate_sample_base64_image(),
            "filename": f"test_image_expiring_{uuid.uuid4()}.png",
            "type": "Image",
            "description": "Test image for expiration testing"
        }
        
        # Create share request with 1 minute expiration
        share_request = {
            "attachment_data": attachment_data,
            "expires_in_minutes": 1  # 1 minute expiration
        }
        
        # Send request to create share
        response = requests.post(
            f"{backend_url}/api/share-attachment",
            json=share_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            share_data = response.json()
            share_id = share_data.get("share_id")
            preview_url = share_data.get("preview_url")
            
            print(f"✅ Short-lived share created successfully (ID: {share_id})")
            print(f"  - Expires in: 1 minute")
            
            # Verify it exists in MongoDB
            verify_mongodb_document(share_id)
            
            # Test access immediately (should work)
            print(f"🔍 Testing immediate access...")
            immediate_response = requests.get(preview_url)
            if immediate_response.status_code == 200:
                print(f"✅ Immediate access successful")
            else:
                print(f"❌ Immediate access failed: {immediate_response.status_code}")
                try:
                    error_data = immediate_response.json()
                    print(f"  - Error: {error_data}")
                except:
                    print(f"  - Response: {immediate_response.text}")
            
            # Wait for expiration (70 seconds to be safe)
            print(f"⏳ Waiting 70 seconds for share to expire...")
            time.sleep(70)
            
            # Test access after expiration (should fail)
            print(f"🔍 Testing access after expiration...")
            expired_response = requests.get(preview_url)
            if expired_response.status_code == 404:
                print(f"✅ Access correctly denied after expiration")
                try:
                    error_data = expired_response.json()
                    print(f"  - Error message: {error_data.get('detail', 'Unknown')}")
                except:
                    print(f"  - Response: {expired_response.text}")
            else:
                print(f"❌ Unexpected response after expiration: {expired_response.status_code}")
                try:
                    response_data = expired_response.json()
                    print(f"  - Response: {response_data}")
                except:
                    print(f"  - Response: {expired_response.text}")
            
            # Check if document was removed from MongoDB
            print(f"🔍 Checking if document was removed from MongoDB...")
            share_doc = db.temporary_shares.find_one({"id": share_id})
            if share_doc:
                print(f"❌ Document still exists in MongoDB after expiration")
                print(f"  - Document: {share_doc}")
            else:
                print(f"✅ Document correctly removed from MongoDB after expiration")
            
            return True
        else:
            print(f"❌ Failed to create short-lived share: {response.status_code}")
            try:
                error_data = response.json()
                print(f"  - Error: {error_data}")
            except:
                print(f"  - Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing expired share: {str(e)}")
        return False

def test_manual_document_creation():
    """Test manually creating a document in the temporary_shares collection"""
    print("\n🔍 Testing manual document creation in MongoDB...")
    
    try:
        # Generate unique share ID
        share_id = str(uuid.uuid4())
        
        # Calculate expiration time (30 minutes from now)
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(minutes=30)
        
        # Create attachment data
        attachment_data = {
            "url": generate_sample_base64_image(),
            "filename": f"test_image_manual_{uuid.uuid4()}.png",
            "type": "Image",
            "description": "Test image for manual document creation"
        }
        
        # Create share document
        share_doc = {
            "id": share_id,
            "attachment_data": attachment_data,
            "created_at": created_at,
            "expires_at": expires_at,
            "access_count": 0
        }
        
        # Insert document
        result = db.temporary_shares.insert_one(share_doc)
        
        if result.acknowledged:
            print(f"✅ Document manually created in MongoDB")
            print(f"  - Share ID: {share_id}")
            print(f"  - Created at: {created_at}")
            print(f"  - Expires at: {expires_at}")
            
            # Generate URLs
            base_url = backend_url
            preview_url = f"{base_url}/api/shared-attachment/{share_id}/preview"
            download_url = f"{base_url}/api/shared-attachment/{share_id}/download"
            
            # Test access
            print(f"🔍 Testing access to manually created share...")
            print(f"  - Preview URL: {preview_url}")
            
            preview_response = requests.get(preview_url)
            if preview_response.status_code == 200:
                print(f"✅ Preview access successful")
            else:
                print(f"❌ Preview access failed: {preview_response.status_code}")
                try:
                    error_data = preview_response.json()
                    print(f"  - Error: {error_data}")
                except:
                    print(f"  - Response: {preview_response.text}")
            
            return True
        else:
            print(f"❌ Failed to manually create document in MongoDB")
            return False
    except Exception as e:
        print(f"❌ Error manually creating document: {str(e)}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n🚀 Running all sharing functionality tests...")
    
    # Check TTL index
    check_ttl_index()
    
    # Check collection contents
    check_collection_contents()
    
    # Create test share
    share_data = create_test_share()
    
    if share_data:
        # Verify MongoDB document
        verify_mongodb_document(share_data.get("share_id"))
        
        # Test share access
        test_share_access(share_data)
    
    # Test expired share
    test_expired_share()
    
    # Test manual document creation
    test_manual_document_creation()
    
    # Final check of collection contents
    check_collection_contents()

if __name__ == "__main__":
    run_all_tests()