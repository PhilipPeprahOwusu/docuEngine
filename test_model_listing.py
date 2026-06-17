#!/usr/bin/env python3
"""
Test script for dynamic model listing endpoint
Tests the /api/v1/settings/api-keys/list-models endpoint
"""
import requests
import json
import sys
from typing import Dict, Any


# Backend URL
BACKEND_URL = "http://136.116.180.162"

# Demo credentials
DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo1234"


def login() -> str:
    """Login and get JWT token"""
    print("🔐 Logging in as demo user...")

    login_data = {
        "username": DEMO_EMAIL,
        "password": DEMO_PASSWORD
    }

    response = requests.post(
        f"{BACKEND_URL}/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"✅ Login successful! Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)


def get_saved_api_keys(token: str) -> Dict[str, Any]:
    """Get saved API keys from the database"""
    print("\n📋 Fetching saved API keys...")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{BACKEND_URL}/api/v1/settings/api-keys",
        headers=headers
    )

    if response.status_code == 200:
        keys = response.json().get("api_keys", [])
        print(f"✅ Found {len(keys)} saved API key(s)")
        for key in keys:
            print(f"   - {key['provider']}: {key['key_preview']} (model: {key['model_name']})")
        return response.json()
    else:
        print(f"❌ Failed to fetch API keys: {response.status_code}")
        print(f"Response: {response.text}")
        return {"api_keys": []}


def test_list_models(token: str, provider: str, api_key: str, model_name: str = ""):
    """Test the list-models endpoint"""
    print(f"\n🧪 Testing dynamic model listing for {provider}...")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "provider": provider,
        "api_key": api_key,
        "model_name": model_name  # Can be empty for listing
    }

    print(f"📤 Request payload:")
    print(f"   Provider: {provider}")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else ''}")
    print(f"   Model Name: {model_name or '(none)'}")

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/settings/api-keys/list-models",
            headers=headers,
            json=payload,
            timeout=60  # Anthropic testing takes time
        )

        print(f"\n📥 Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            if data.get("success"):
                models = data.get("models", [])
                print(f"✅ SUCCESS! Found {len(models)} available model(s):\n")

                for i, model in enumerate(models, 1):
                    print(f"   {i}. {model}")

                # Map model names to friendly names
                print(f"\n📊 Model Mapping (Anthropic Console → API):")
                model_mapping = {
                    "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet (Oct 2024)",
                    "claude-3-5-sonnet-20240620": "Claude 3.5 Sonnet (Jun 2024) - Sonnet 4.6",
                    "claude-3-5-haiku-20241022": "Claude 3.5 Haiku (Oct 2024)",
                    "claude-3-opus-20240229": "Claude 3 Opus (Feb 2024) - Opus 4.8",
                    "claude-3-sonnet-20240229": "Claude 3 Sonnet (Feb 2024)",
                    "claude-3-haiku-20240307": "Claude 3 Haiku (Mar 2024) - Haiku 4.5"
                }

                for model in models:
                    friendly_name = model_mapping.get(model, model)
                    print(f"   {model} → {friendly_name}")

                return data
            else:
                print(f"❌ FAILED: {data.get('message', 'Unknown error')}")
                return data
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print(f"⏱️  Request timed out (this is normal for Anthropic - testing 6 models takes time)")
        print(f"The backend is still processing. Check backend logs for results.")
        return None
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None


def test_api_key(token: str, provider: str, api_key: str, model_name: str):
    """Test a specific API key and model"""
    print(f"\n🧪 Testing API key with model {model_name}...")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "provider": provider,
        "api_key": api_key,
        "model_name": model_name
    }

    response = requests.post(
        f"{BACKEND_URL}/api/v1/settings/api-keys/test",
        headers=headers,
        json=payload,
        timeout=30
    )

    print(f"📥 Response Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        if data.get("success"):
            print(f"✅ {data.get('message')}")
            print(f"📝 Test Response: {data.get('test_response', '')}")
            return True
        else:
            print(f"❌ {data.get('message')}")
            print(f"Error: {data.get('error', '')}")
            return False
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"Response: {response.text}")
        return False


def main():
    """Main test flow"""
    print("=" * 60)
    print("🚀 DocuEngine Dynamic Model Listing - Backend Test")
    print("=" * 60)

    # Step 1: Login
    token = login()

    # Step 2: Get saved API keys
    saved_keys = get_saved_api_keys(token)

    # Step 3: Check if Anthropic key exists
    anthropic_key = None
    for key in saved_keys.get("api_keys", []):
        if key["provider"] == "anthropic":
            print(f"\n⚠️  Found saved Anthropic API key: {key['key_preview']}")
            print(f"⚠️  However, the encrypted key cannot be retrieved via API")
            print(f"\n💡 To test dynamic model listing, you need to provide your API key:")
            print(f"   Run this script with your API key as an argument:")
            print(f"   python test_model_listing.py <your-anthropic-api-key>")

            if len(sys.argv) > 1:
                api_key = sys.argv[1]
                print(f"\n🔑 Using provided API key from command line")

                # Test listing models
                result = test_list_models(token, "anthropic", api_key, "")

                if result and result.get("success") and result.get("models"):
                    # Test the first available model
                    first_model = result["models"][0]
                    print(f"\n" + "=" * 60)
                    print(f"Testing first available model: {first_model}")
                    print("=" * 60)
                    test_api_key(token, "anthropic", api_key, first_model)

                return
            else:
                print(f"\n❌ No API key provided. Exiting.")
                return

    print(f"\n❌ No Anthropic API key found in database")
    print(f"💡 Please save your API key first in Settings, or provide it as argument:")
    print(f"   python test_model_listing.py <your-anthropic-api-key>")


if __name__ == "__main__":
    main()
