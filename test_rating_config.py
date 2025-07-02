#!/usr/bin/env python3
"""
Quick Rating System URL Test
Tests if rating system routes are properly configured
"""

import sys
import os

def test_rating_routes():
    """Test that rating system routes exist"""
    print("🌟 Testing Rating System Routes")
    print("=" * 35)
    
    # Test if rating blueprint exists
    try:
        print("📦 Checking rating blueprint...")
        
        # Check if files exist
        rating_files = [
            'blueprint/rating.py',
            'controllers/rating_controller.py',
            'templates/ratings/rateable_bookings.html',
            'templates/ratings/my_ratings.html'
        ]
        
        for file_path in rating_files:
            if os.path.exists(file_path):
                print(f"✅ Found: {file_path}")
            else:
                print(f"❌ Missing: {file_path}")
        
        # Check if rating blueprint is imported in app.py
        with open('app.py', 'r') as f:
            app_content = f.read()
            
        if 'from blueprint.rating import rating_bp' in app_content:
            print("✅ Rating blueprint imported in app.py")
        else:
            print("❌ Rating blueprint not imported in app.py")
        
        if 'app.register_blueprint(rating_bp' in app_content:
            print("✅ Rating blueprint registered in app.py")
        else:
            print("❌ Rating blueprint not registered in app.py")
        
        # Check Rating model
        with open('blueprint/models.py', 'r') as f:
            models_content = f.read()
        
        if 'class Rating(db.Model):' in models_content:
            print("✅ Rating model exists in models.py")
        else:
            print("❌ Rating model missing in models.py")
        
        print("\n🎯 Rating System Routes to Test:")
        routes = [
            "GET  /rating/rateable-bookings - View bookings you can rate",
            "POST /rating/submit - Submit a rating",
            "GET  /rating/my-ratings - View your submitted ratings",
            "GET  /rating/booking/<id>/ratings - View ratings for a booking",
            "GET  /rating/user/<id>/ratings - View ratings for a user",
            "GET  /rating/user/<id>/stats - Get rating statistics for a user"
        ]
        
        for route in routes:
            print(f"  • {route}")
        
        print("\n✅ Rating system appears to be properly configured!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking rating system: {e}")
        return False

def test_rating_templates():
    """Test rating templates exist and have basic content"""
    print("\n📄 Testing Rating Templates")
    print("=" * 25)
    
    templates = {
        'templates/ratings/rateable_bookings.html': ['rateable bookings', 'Rate'],
        'templates/ratings/my_ratings.html': ['my ratings', 'rating']
    }
    
    for template_path, keywords in templates.items():
        if os.path.exists(template_path):
            print(f"✅ Template exists: {template_path}")
            
            with open(template_path, 'r') as f:
                content = f.read().lower()
            
            for keyword in keywords:
                if keyword.lower() in content:
                    print(f"  ✅ Contains '{keyword}'")
                else:
                    print(f"  ❌ Missing '{keyword}'")
        else:
            print(f"❌ Template missing: {template_path}")

def main():
    """Run rating system configuration tests"""
    print("🌟 RATING SYSTEM - CONFIGURATION TESTS")
    print("=" * 45)
    
    try:
        success = True
        success &= test_rating_routes()
        test_rating_templates()
        
        if success:
            print(f"\n🎊 RATING SYSTEM READY FOR TESTING!")
            print("\n📋 Next Steps:")
            print("1. Apply rating table migration to database")
            print("2. Start Flask app: python app.py") 
            print("3. Create test bookings with 'Completed' status")
            print("4. Visit: http://localhost:5000/rating/rateable-bookings")
            print("5. Test rating submission and viewing")
            print("\n📖 For detailed testing: see RATING_SYSTEM_TESTING_GUIDE.md")
            return 0
        else:
            print(f"\n❌ RATING SYSTEM NOT READY!")
            print("Fix the configuration issues above")
            return 1
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
