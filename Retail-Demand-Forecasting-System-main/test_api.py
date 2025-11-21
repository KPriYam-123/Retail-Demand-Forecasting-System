"""
Quick Test Script for API
==========================
Run this to test if your backend is working correctly.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_root():
    """Test root endpoint"""
    print("Testing / endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_stats():
    """Test stats endpoint (will fail if no data uploaded)"""
    print("Testing /stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    print()

def main():
    print("=" * 60)
    print("API Test Script")
    print("=" * 60)
    print(f"Testing API at: {BASE_URL}")
    print()
    
    try:
        test_root()
        test_health()
        test_stats()
        
        print("=" * 60)
        print("✓ API is running!")
        print("=" * 60)
        print()
        print("To fully test:")
        print("1. Upload a dataset via the frontend")
        print("2. Run /forecast endpoint")
        print("3. Check /products endpoint")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API!")
        print("Make sure the backend is running on port 8000")
        print("Run: cd backend/app && python main.py")

if __name__ == "__main__":
    main()
