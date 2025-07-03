#!/usr/bin/env python3
"""
Test the rating system API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_rating_endpoints():
    """Test rating system endpoints"""
    
    print("🌟 Testing Rating System Endpoints")
    print("=" * 50)
    
    # Test 1: Get rateable bookings (should redirect to login if not authenticated)
    print("\n📝 Test 1: Access rateable bookings (unauthenticated)")
    response = requests.get(f"{BASE_URL}/rating/rateable-bookings")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 302:
        print("✅ Correctly redirected to login (authentication required)")
    else:
        print(f"Response: {response.text[:200]}...")
    
    # Test 2: Try to access user rating stats
    print("\n📊 Test 2: Access user rating stats")
    response = requests.get(f"{BASE_URL}/rating/user/101/stats")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"✅ User 101 rating stats: {data}")
        except:
            print(f"Response: {response.text[:200]}...")
    else:
        print(f"Response: {response.text[:100]}...")
    
    # Test 3: Check if rating view exists for user
    print("\n🔍 Test 3: Access user ratings view")
    response = requests.get(f"{BASE_URL}/rating/user/101/ratings")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Rating view accessible")
        print(f"Response length: {len(response.text)} characters")
    else:
        print(f"Response: {response.text[:100]}...")
    
    # Test 4: Check existing rating from our test data
    print("\n⭐ Test 4: Check existing ratings")
    response = requests.get(f"{BASE_URL}/rating/user/105/ratings")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Found ratings for user 105 (Eve)")
        print(f"Response contains rating info: {'rating' in response.text.lower()}")
    
    print("\n🎉 Rating system endpoint tests completed!")

if __name__ == "__main__":
    test_rating_endpoints()
