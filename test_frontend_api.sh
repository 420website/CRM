#!/bin/bash

# Test frontend data loading by checking browser console
echo "🧪 Testing frontend data loading..."

# Create a simple test HTML page to check API calls
cat > /tmp/test_api.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>API Test</title>
</head>
<body>
    <h1>API Connection Test</h1>
    <div id="results"></div>
    
    <script>
        const API_URL = 'https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com';
        const results = document.getElementById('results');
        
        async function testAPIs() {
            try {
                console.log('🔍 Testing dispositions API...');
                const dispositionsResponse = await fetch(`${API_URL}/api/dispositions`);
                const dispositions = await dispositionsResponse.json();
                console.log('✅ Dispositions:', dispositions.length, 'items');
                console.log('📋 First 5 dispositions:', dispositions.slice(0, 5).map(d => d.name));
                
                results.innerHTML += `<p>✅ Dispositions: ${dispositions.length} items</p>`;
                results.innerHTML += `<p>📋 First 5: ${dispositions.slice(0, 5).map(d => d.name).join(', ')}</p>`;
                
                console.log('🔍 Testing referral sites API...');
                const referralSitesResponse = await fetch(`${API_URL}/api/referral-sites`);
                const referralSites = await referralSitesResponse.json();
                console.log('✅ Referral Sites:', referralSites.length, 'items');
                console.log('📋 First 5 referral sites:', referralSites.slice(0, 5).map(s => s.name));
                
                results.innerHTML += `<p>✅ Referral Sites: ${referralSites.length} items</p>`;
                results.innerHTML += `<p>📋 First 5: ${referralSites.slice(0, 5).map(s => s.name).join(', ')}</p>`;
                
            } catch (error) {
                console.error('❌ Error:', error);
                results.innerHTML += `<p>❌ Error: ${error.message}</p>`;
            }
        }
        
        testAPIs();
    </script>
</body>
</html>
EOF

echo "✅ Created test HTML file at /tmp/test_api.html"
echo "🌐 You can test the API connectivity by opening this file in a browser"
echo "📋 The test will show if the frontend can successfully fetch data from the APIs"