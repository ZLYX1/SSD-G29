#!/usr/bin/env python3
"""
Test Flask app routing
"""
import requests

BASE_URL = "http://localhost:5000"

def test_flask_routes():
    """Test various Flask routes to see what's available"""
    
    print("🔍 Testing Flask Application Routes")
    print("=" * 50)
    
    routes_to_test = [
        "/",
        "/auth",
        "/auth?mode=login",
        "/rating/user/105/stats", 
        "/rating/user/105/ratings",
        "/rating/rateable-bookings",
        "/browse",
        "/profile"
    ]
    
    for route in routes_to_test:
        try:
            response = requests.get(f"{BASE_URL}{route}", timeout=5)
            print(f"\n📍 Route: {route}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Accessible")
                if 'rating' in route:
                    # Check if it contains rating-related content
                    content_lower = response.text.lower()
                    has_rating = 'rating' in content_lower
                    has_star = 'star' in content_lower
                    has_feedback = 'feedback' in content_lower
                    print(f"   🌟 Contains rating content: {has_rating}")
                    print(f"   ⭐ Contains stars: {has_star}")
                    print(f"   💭 Contains feedback: {has_feedback}")
                    
            elif response.status_code == 302:
                print("   🔄 Redirected (likely to login)")
            elif response.status_code == 404:
                print("   ❌ Not found")
            else:
                print(f"   ⚠️  Other status: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Error: {e}")
    
    print(f"\n🎉 Route testing completed!")

if __name__ == "__main__":
    test_flask_routes()
