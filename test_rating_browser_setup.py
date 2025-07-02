#!/usr/bin/env python3
"""
Complete Rating System Test with Browser Testing Guide
This script will help verify the rating system is working correctly
"""

import sys
import os
import subprocess
import time
import json
from datetime import datetime, timedelta

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking Prerequisites...")
    print("=" * 30)
    
    # Check if all files exist
    required_files = [
        'blueprint/rating.py',
        'controllers/rating_controller.py', 
        'templates/ratings/rateable_bookings.html',
        'templates/ratings/my_ratings.html',
        'rating_system_migration.sql'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    
    # Check if Rating model is in app.py imports
    with open('app.py', 'r') as f:
        app_content = f.read()
    
    if 'Rating' in app_content and 'rating_bp' in app_content:
        print("✅ Rating system integrated in app.py")
    else:
        print("❌ Rating system not properly integrated in app.py")
        return False
    
    print("✅ All prerequisites met!")
    return True

def create_test_data_script():
    """Create a script to add test data"""
    test_data_script = '''
-- Test data for rating system
-- Run this after applying the rating migration

-- Ensure we have test users (if not already created)
INSERT INTO "user" (id, email, password_hash, role, gender, active, email_verified) VALUES
(101, 'test_seeker@example.com', 'pbkdf2:sha256:260000$test$test', 'seeker', 'Male', true, true),
(102, 'test_escort@example.com', 'pbkdf2:sha256:260000$test$test', 'escort', 'Female', true, true)
ON CONFLICT (id) DO NOTHING;

-- Create profiles for test users
INSERT INTO profile (user_id, name, bio, age, preference) VALUES
(101, 'Test Seeker', 'Test seeker for rating system', 25, 'Female'),
(102, 'Test Escort', 'Test escort for rating system', 28, 'Male')
ON CONFLICT (user_id) DO NOTHING;

-- Create a completed booking for testing
INSERT INTO booking (id, seeker_id, escort_id, start_time, end_time, status) VALUES
(201, 101, 102, NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour', 'Completed')
ON CONFLICT (id) DO NOTHING;

-- Create another completed booking  
INSERT INTO booking (id, seeker_id, escort_id, start_time, end_time, status) VALUES
(202, 101, 102, NOW() - INTERVAL '1 day', NOW() - INTERVAL '23 hours', 'Completed')
ON CONFLICT (id) DO NOTHING;

-- Verify test data
SELECT 'Users:' as type, id, email, role FROM "user" WHERE id IN (101, 102)
UNION ALL
SELECT 'Bookings:', id::text, status, 'completed' FROM booking WHERE id IN (201, 202);
'''
    
    with open('test_data_rating.sql', 'w') as f:
        f.write(test_data_script)
    
    print("📝 Created test_data_rating.sql")
    return True

def test_flask_startup():
    """Test if Flask app can start without errors"""
    print("\n🚀 Testing Flask App Startup...")
    print("=" * 30)
    
    try:
        # Try to import the main components
        print("📦 Testing imports...")
        
        # Test the rating controller import
        sys.path.insert(0, '.')
        
        # This will fail if there are syntax errors
        from controllers.rating_controller import RatingController
        print("✅ RatingController imports successfully")
        
        # Test rating model
        from blueprint.models import Rating
        print("✅ Rating model imports successfully")
        
        # Test utilities
        from datetime import datetime
        print("✅ Required utilities available")
        
        print("✅ Flask app should start successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def generate_browser_test_guide():
    """Generate step-by-step browser testing guide"""
    guide = '''
# 🌟 RATING SYSTEM - BROWSER TESTING GUIDE

## 🚀 Step 1: Database Setup

### 1.1 Apply Rating Migration
```sql
-- Run in your PostgreSQL database:
-- (Copy from rating_system_migration.sql)
```

### 1.2 Add Test Data
```sql
-- Run the test data script:
-- (Copy from test_data_rating.sql)
```

## 🌐 Step 2: Start Flask Application

### 2.1 Start the Server
```bash
python app.py
```

### 2.2 Expected Output
```
[INFO] Connecting to DB host: db
[INFO] DB port: 5432
[INFO] DB name: ssd_database
* Running on http://127.0.0.1:5000
```

## 🧪 Step 3: Browser Testing

### 3.1 Login as Test User
- **URL**: http://localhost:5000/auth?mode=login
- **Email**: test_seeker@example.com  
- **Password**: test (or whatever you set)

### 3.2 View Rateable Bookings
- **URL**: http://localhost:5000/rating/rateable-bookings
- **Expected**: See completed bookings that can be rated
- **Should Show**: Booking details, "Rate" buttons

### 3.3 Submit a Rating
- **Click**: "Rate" button on a booking
- **Fill Form**:
  - Rating: 5 stars
  - Feedback: "Excellent service, very professional!"
- **Submit**: Form should redirect with success message

### 3.4 View Your Ratings  
- **URL**: http://localhost:5000/rating/my-ratings
- **Expected**: See the rating you just submitted
- **Should Show**: Rating stars, feedback, date

### 3.5 Check Rating Statistics
- **URL**: http://localhost:5000/rating/user/102/stats
- **Expected**: JSON with rating statistics
- **Should Show**: {"average_rating": 5.0, "total_ratings": 1}

## ✅ Success Indicators

### Visual Confirmations:
- [ ] ⭐ Star rating selector works (clickable stars)
- [ ] 📝 Feedback textarea accepts input
- [ ] 🚀 Form submits without errors
- [ ] ✅ Success message appears after submission
- [ ] 📊 Ratings display correctly on pages
- [ ] 🔄 Already rated bookings don't appear in rateable list

### Functional Tests:
- [ ] Can only rate completed bookings
- [ ] Cannot rate same booking twice
- [ ] Rating must be 1-5 stars
- [ ] Average rating calculates correctly
- [ ] Only own bookings appear for rating

## 🐛 Troubleshooting

### Issue: "404 Not Found" on rating URLs
**Solution**: Ensure rating blueprint is registered in app.py

### Issue: "No rateable bookings found"
**Solution**: Create test bookings with status='Completed' and past end_time

### Issue: Rating form doesn't submit
**Solution**: Check CSRF token and form validation

### Issue: Database errors
**Solution**: Apply rating_system_migration.sql first

## 📸 What You Should See

### Rateable Bookings Page:
```html
<h2>Bookings You Can Rate</h2>
<div class="booking-card">
  <p>Booking with Test Escort</p>
  <p>Date: [booking date]</p>
  <button>Rate This Booking</button>
</div>
```

### Rating Form:
```html
<form>
  <div class="star-rating">
    ⭐⭐⭐⭐⭐ (clickable)
  </div>
  <textarea placeholder="Share your experience..."></textarea>
  <button>Submit Rating</button>
</form>
```

### My Ratings Page:
```html
<h2>My Ratings</h2>
<div class="rating-item">
  <p>⭐⭐⭐⭐⭐ for Test Escort</p>
  <p>"Excellent service, very professional!"</p>
  <p>Rated on: [date]</p>
</div>
```
'''
    
    with open('BROWSER_TESTING_GUIDE.md', 'w') as f:
        f.write(guide)
    
    print("📖 Created BROWSER_TESTING_GUIDE.md")

def main():
    """Run all pre-testing checks and generate guides"""
    print("🌟 RATING SYSTEM - COMPLETE TESTING SETUP")
    print("=" * 50)
    
    success = True
    
    # Run all checks
    success &= check_prerequisites()
    success &= test_flask_startup() 
    
    # Generate test resources
    create_test_data_script()
    generate_browser_test_guide()
    
    if success:
        print(f"\n🎊 RATING SYSTEM READY FOR BROWSER TESTING!")
        print("\n📋 Next Steps:")
        print("1. Apply database migrations:")
        print("   - Run: rating_system_migration.sql")
        print("   - Run: test_data_rating.sql")
        print("2. Start Flask app: python app.py")
        print("3. Follow: BROWSER_TESTING_GUIDE.md")
        print("4. Test URLs:")
        print("   - http://localhost:5000/auth?mode=login")
        print("   - http://localhost:5000/rating/rateable-bookings")
        print("   - http://localhost:5000/rating/my-ratings")
        
        print(f"\n🎯 Key Test Points:")
        print("- Login with test user credentials")
        print("- View completed bookings available for rating")
        print("- Submit 5-star rating with feedback")
        print("- Verify rating appears in 'My Ratings'")
        print("- Check rating statistics")
        
        return 0
    else:
        print(f"\n❌ SETUP ISSUES FOUND!")
        print("Fix the issues above before browser testing")
        return 1

if __name__ == "__main__":
    sys.exit(main())
