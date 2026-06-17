#!/bin/bash

echo "=========================================="
echo "Testing Dynamic Model Listing Backend"
echo "=========================================="

# Step 1: Login
echo ""
echo "Step 1: Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST http://136.116.180.162/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo@example.com&password=demo1234")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo "✅ Login successful!"
echo "Token: ${TOKEN:0:30}..."

# Step 2: Get saved API keys
echo ""
echo "=========================================="
echo "Step 2: Getting saved API keys..."
echo "=========================================="
API_KEYS_RESPONSE=$(curl -s -X GET http://136.116.180.162/api/v1/settings/api-keys \
  -H "Authorization: Bearer $TOKEN")

echo "$API_KEYS_RESPONSE" | python3 -m json.tool

# Check if Anthropic key exists
HAS_ANTHROPIC=$(echo $API_KEYS_RESPONSE | grep -o '"provider":"anthropic"' | wc -l)

if [ "$HAS_ANTHROPIC" -gt 0 ]; then
    echo ""
    echo "✅ Found Anthropic API key in database"
    echo ""
    echo "⚠️  Note: The encrypted key cannot be retrieved via API"
    echo "To test dynamic model listing, you need to provide your API key"
    echo ""
    read -p "Enter your Anthropic API key (or press Enter to skip): " ANTHROPIC_KEY

    if [ ! -z "$ANTHROPIC_KEY" ]; then
        echo ""
        echo "=========================================="
        echo "Step 3: Testing Dynamic Model Listing"
        echo "=========================================="
        echo "Testing /api/v1/settings/api-keys/list-models endpoint..."
        echo "This may take 30-60 seconds as it tests multiple models..."
        echo ""

        MODEL_LIST_RESPONSE=$(curl -s -X POST http://136.116.180.162/api/v1/settings/api-keys/list-models \
          -H "Authorization: Bearer $TOKEN" \
          -H "Content-Type: application/json" \
          -d "{\"provider\":\"anthropic\",\"api_key\":\"$ANTHROPIC_KEY\",\"model_name\":\"\"}" \
          --max-time 120)

        echo "$MODEL_LIST_RESPONSE" | python3 -m json.tool

        # Check if successful
        IS_SUCCESS=$(echo $MODEL_LIST_RESPONSE | grep -o '"success":true' | wc -l)

        if [ "$IS_SUCCESS" -gt 0 ]; then
            echo ""
            echo "✅ SUCCESS! Dynamic model listing works!"
            echo ""

            # Extract and display models
            MODELS=$(echo $MODEL_LIST_RESPONSE | python3 -c "import sys, json; data = json.load(sys.stdin); print('\n'.join(data.get('models', [])))" 2>/dev/null)

            if [ ! -z "$MODELS" ]; then
                echo "Available models for your API key:"
                echo "$MODELS" | nl

                # Test the first model
                FIRST_MODEL=$(echo "$MODELS" | head -1)
                echo ""
                echo "=========================================="
                echo "Step 4: Testing API Key with Model"
                echo "=========================================="
                echo "Testing model: $FIRST_MODEL"
                echo ""

                TEST_RESPONSE=$(curl -s -X POST http://136.116.180.162/api/v1/settings/api-keys/test \
                  -H "Authorization: Bearer $TOKEN" \
                  -H "Content-Type: application/json" \
                  -d "{\"provider\":\"anthropic\",\"api_key\":\"$ANTHROPIC_KEY\",\"model_name\":\"$FIRST_MODEL\"}" \
                  --max-time 30)

                echo "$TEST_RESPONSE" | python3 -m json.tool
            fi
        else
            echo ""
            echo "❌ Model listing failed"
        fi
    else
        echo "Skipping model listing test"
    fi
else
    echo ""
    echo "⚠️  No Anthropic API key found in database"
    echo "Please save your API key first in Settings"
fi

echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="
