#!/usr/bin/env python3
"""
Test the correct rating routes
"""
import requests

BASE_URL = "http://localhost:5000"

def test_correct_rating_routes():
    """Test the actual rating routes"""
    
    print("🌟 Testing Correct Rating System Routes")
    print("=" * 50)
    
    routes_to_test = [
        "/rating/rateable-bookings",
        "/rating/my-ratings", 
        "/rating/user/105",
        "/rating/user/101",
        "/rating/booking/203",  # Our test booking with a rating
    ]
    
    for route in routes_to_test:
        try:
            response = requests.get(f"{BASE_URL}{route}", timeout=5)
            print(f"\n📍 Route: {route}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                # Check if it's actually the auth page (redirect)
                if 'login' in response.text.lower() and 'password' in response.text.lower():
                    print("   🔐 Redirected to login (authentication required)")
                else:
                    print("   ✅ Accessible with content")
                    # Check for rating-related content
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
    
    print(f"\n🎉 Correct route testing completed!")

if __name__ == "__main__":
    test_correct_rating_routes()
