#!/usr/bin/env python3
"""
Comprehensive Rating System Demo with Session
"""
import requests
import json
from datetime import datetime

class RatingSystemDemo:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.session = requests.Session()
        
    def login(self, email, password):
        """Login and maintain session"""
        print(f"🔐 Logging in as {email}")
        
        # Get login page to extract any CSRF tokens
        login_page = self.session.get(f"{self.base_url}/auth?mode=login")
        print(f"   Login page status: {login_page.status_code}")
        
        # Attempt login
        login_data = {
            'email': email,
            'password': password,
            'submit': 'Login'
        }
        
        response = self.session.post(f"{self.base_url}/auth?mode=login", data=login_data)
        print(f"   Login response status: {response.status_code}")
        
        # Check if login was successful
        if 'dashboard' in response.text.lower() or 'logout' in response.text.lower():
            print("   ✅ Login successful!")
            return True
        elif response.status_code == 302:
            print("   🔄 Redirected (possibly successful)")
            return True
        else:
            print("   ❌ Login may have failed")
            print(f"   Response contains 'login': {'login' in response.text.lower()}")
            return False
    
    def test_rateable_bookings(self):
        """Test viewing rateable bookings"""
        print("\n📋 Testing Rateable Bookings")
        print("-" * 40)
        
        response = self.session.get(f"{self.base_url}/rating/rateable-bookings")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text.lower()
            if 'login' in content and 'password' in content:
                print("❌ Still redirected to login - authentication failed")
                return False
            else:
                print("✅ Accessed rateable bookings page")
                # Check for booking-related content
                has_booking = 'booking' in content
                has_rate = 'rate' in content or 'rating' in content
                has_submit = 'submit' in content
                print(f"   📝 Contains booking info: {has_booking}")
                print(f"   🌟 Contains rating elements: {has_rate}")
                print(f"   🔘 Contains submit elements: {has_submit}")
                return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
    
    def test_user_ratings(self, user_id):
        """Test viewing user ratings"""
        print(f"\n👤 Testing User {user_id} Ratings")
        print("-" * 40)
        
        response = self.session.get(f"{self.base_url}/rating/user/{user_id}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text.lower()
            if 'login' in content and 'password' in content:
                print("❌ Still redirected to login")
                return False
            else:
                print("✅ Accessed user ratings page")
                has_rating = 'rating' in content
                has_star = 'star' in content
                has_feedback = 'feedback' in content
                print(f"   🌟 Contains rating content: {has_rating}")
                print(f"   ⭐ Contains star content: {has_star}")
                print(f"   💭 Contains feedback content: {has_feedback}")
                return True
        else:
            print(f"❌ Status code: {response.status_code}")
            return False
    
    def test_my_ratings(self):
        """Test viewing my submitted ratings"""
        print(f"\n📊 Testing My Ratings")
        print("-" * 40)
        
        response = self.session.get(f"{self.base_url}/rating/my-ratings")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text.lower()
            if 'login' in content and 'password' in content:
                print("❌ Still redirected to login")
                return False
            else:
                print("✅ Accessed my ratings page")
                has_rating = 'rating' in content
                has_submitted = 'submitted' in content or 'gave' in content
                print(f"   🌟 Contains rating content: {has_rating}")
                print(f"   📤 Contains submission info: {has_submitted}")
                return True
        else:
            print(f"❌ Status code: {response.status_code}")
            return False
    
    def simulate_rating_submission(self, booking_id, rating_value, feedback):
        """Test rating submission"""
        print(f"\n⭐ Testing Rating Submission for Booking {booking_id}")
        print("-" * 50)
        
        rating_data = {
            'booking_id': booking_id,
            'rating': rating_value,
            'feedback': feedback
        }
        
        response = self.session.post(f"{self.base_url}/rating/submit", data=rating_data)
        print(f"Submission status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Rating submission response: {result}")
                return result.get('success', False)
            except:
                print("✅ Rating submitted (non-JSON response)")
                return True
        elif response.status_code == 302:
            print("🔄 Redirected after submission (likely successful)")
            return True
        else:
            print(f"❌ Submission failed with status {response.status_code}")
            return False

def main():
    print("🌟 RATING SYSTEM COMPREHENSIVE DEMO")
    print("=" * 60)
    
    demo = RatingSystemDemo()
    
    # Test with our created test user
    print("\n🔐 Phase 1: Authentication")
    login_success = demo.login('testuser@example.com', 'password123')
    
    if not login_success:
        print("❌ Login failed. Testing with public endpoints only.")
        print("\n📊 Testing Public User Rating Views")
        demo.test_user_ratings(105)  # User with existing rating
        demo.test_user_ratings(101)  # User without ratings
        return
    
    print("\n📋 Phase 2: Authenticated Rating System Tests")
    
    # Test authenticated endpoints
    demo.test_rateable_bookings()
    demo.test_my_ratings()
    demo.test_user_ratings(105)
    demo.test_user_ratings(101)
    
    print("\n⭐ Phase 3: Rating Submission Test")
    # Try to submit a rating for one of our test bookings
    demo.simulate_rating_submission(31, 5, "Excellent service! Very professional and punctual.")
    
    print("\n🎉 Demo completed!")
    print("\n📋 Manual Testing Instructions:")
    print("1. Open browser to: http://localhost:5000/auth?mode=login")
    print("2. Login with: testuser@example.com / password123")
    print("3. Visit: http://localhost:5000/rating/rateable-bookings")
    print("4. Submit ratings for the available bookings")
    print("5. View your ratings: http://localhost:5000/rating/my-ratings")
    print("6. View user profiles: http://localhost:5000/rating/user/105")

if __name__ == "__main__":
    main()
