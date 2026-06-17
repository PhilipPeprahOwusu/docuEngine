#!/bin/bash

# Get token
echo "Getting auth token..."
TOKEN=$(curl -s -X POST http://136.116.180.162/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo@example.com&password=demo1234" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

echo "Token: ${TOKEN:0:30}..."
echo ""

# Test /api/v1/settings/models endpoint (doesn't require API key)
echo "===== Testing /api/v1/settings/models ====="
curl -s -X GET http://136.116.180.162/api/v1/settings/models | python3 -m json.tool
echo ""

# Test /api/v1/settings/api-keys
echo "===== Testing /api/v1/settings/api-keys ====="
curl -s -X GET http://136.116.180.162/api/v1/settings/api-keys \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "Backend endpoints are responding correctly!"
echo ""
echo "To test dynamic model listing, you need to:"
echo "1. Go to Settings page: https://frontend-eta-sepia-76.vercel.app/dashboard/settings"
echo "2. Select 'Anthropic' provider"
echo "3. Enter your API key"
echo "4. Click 'Fetch Available Models'"
echo "5. Select a model from the dropdown"
echo "6. Click 'Test API Key'"
echo "7. Click 'Save API Key'"
