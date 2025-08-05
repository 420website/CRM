#!/bin/bash

# EMERGENCY PRODUCTION API ROUTING FIX

echo "🚨 EMERGENCY PRODUCTION API ROUTING FIX"
echo "=================================="

# 1. Check current backend status
echo "1. Checking backend status..."
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8001/api/clinical-templates")
echo "Internal backend HTTP status: $BACKEND_STATUS"

if [ "$BACKEND_STATUS" = "200" ]; then
    echo "✅ Backend is running correctly internally"
    # Get count of templates
    TEMPLATE_COUNT=$(curl -s "http://localhost:8001/api/clinical-templates" | jq length)
    echo "✅ Clinical templates available: $TEMPLATE_COUNT"
    
    # Show first template name
    FIRST_TEMPLATE=$(curl -s "http://localhost:8001/api/clinical-templates" | jq -r '.[0].name')
    echo "✅ First template: $FIRST_TEMPLATE"
else
    echo "❌ Backend is not responding correctly"
    exit 1
fi

# 2. Test external API access
echo ""
echo "2. Testing external API access..."
EXTERNAL_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://my420.ca/api/clinical-templates")
echo "External API HTTP status: $EXTERNAL_STATUS"

if [ "$EXTERNAL_STATUS" = "200" ]; then
    echo "✅ External API is working"
else
    echo "❌ External API is not working (Status: $EXTERNAL_STATUS)"
    echo "This indicates a routing/proxy issue in production"
fi

# 3. Check if we need to use different URL structure
echo ""
echo "3. Checking URL structure..."

# Try different possible URLs
URLs=(
    "https://my420.ca/api/clinical-templates"
    "https://my420.ca:8001/api/clinical-templates"
    "https://my420.ca/backend/api/clinical-templates"
)

for url in "${URLs[@]}"; do
    echo "Testing: $url"
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "failed")
    echo "Status: $status"
    if [ "$status" = "200" ]; then
        echo "✅ Found working URL: $url"
        WORKING_URL="$url"
        break
    fi
done

# 4. Update frontend .env with working URL
if [ -n "$WORKING_URL" ]; then
    echo ""
    echo "4. Updating frontend .env with working URL..."
    BACKEND_BASE_URL=$(echo "$WORKING_URL" | sed 's|/api/clinical-templates||')
    echo "Setting REACT_APP_BACKEND_URL to: $BACKEND_BASE_URL"
    
    # Update .env file
    echo "REACT_APP_BACKEND_URL=$BACKEND_BASE_URL" > /app/frontend/.env
    echo "WDS_SOCKET_PORT=443" >> /app/frontend/.env
    
    # Restart frontend
    sudo supervisorctl restart frontend
    echo "✅ Frontend restarted with correct URL"
else
    echo "❌ No working external URL found"
    echo "This is a production deployment configuration issue"
    echo "The external domain is not properly routing API requests to the backend"
fi

# 5. Final verification
echo ""
echo "5. Final verification..."
echo "Backend data available:"
echo "- Clinical templates: $TEMPLATE_COUNT"
echo "- Dispositions: $(curl -s 'http://localhost:8001/api/dispositions' | jq length)"
echo "- Referral sites: $(curl -s 'http://localhost:8001/api/referral-sites' | jq length)"
echo "- Notes templates: $(curl -s 'http://localhost:8001/api/notes-templates' | jq length)"

echo ""
echo "🎯 USER SHOULD NOW:"
echo "1. Hard refresh browser (Ctrl+F5)"
echo "2. Check if dropdowns are populated"
echo "3. If still not working, there's a production deployment routing issue"

echo ""
echo "🚨 IF STILL NOT WORKING:"
echo "The issue is that the production deployment is not properly configured"
echo "to route /api requests from the external domain to the backend service."
echo "This requires infrastructure/deployment configuration changes."