#!/usr/bin/env python3
"""
Create test bookings and ratings for demonstration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from blueprint.models import User, Booking, Rating
from datetime import datetime, timedelta
import random

def create_test_ratings():
    """Create test bookings and ratings"""
    with app.app_context():
        print("🔧 Creating test bookings and ratings...")
        
        # Get users
        seeker = User.query.filter_by(email='seeker@example.com').first()
        escorts = User.query.filter_by(role='escort').all()
        
        if not seeker or not escorts:
            print("❌ Missing users. Please run create_test_escorts.py first")
            return False
        
        print(f"Found seeker: {seeker.email}")
        print(f"Found {len(escorts)} escorts")
        
        # Create some test bookings (past dates so they can be rated)
        test_bookings = []
        for i, escort in enumerate(escorts[:2]):  # Only create for first 2 escorts
            # Create a completed booking from 2 weeks ago
            start_time = datetime.utcnow() - timedelta(days=14 + i)
            end_time = start_time + timedelta(hours=2)
            
            booking = Booking(
                seeker_id=seeker.id,
                escort_id=escort.id,
                start_time=start_time,
                end_time=end_time,
                status='Completed'
            )
            
            db.session.add(booking)
            test_bookings.append((booking, escort))
            print(f"✅ Created booking with {escort.email}")
        
        # Flush to get booking IDs
        db.session.flush()
        
        # Create ratings for the bookings
        sample_feedbacks = [
            "Excellent service! Professional and friendly. Would definitely book again.",
            "Great experience. Very accommodating and punctual. Highly recommended.",
            "Professional and respectful. Made me feel comfortable throughout.",
            "Outstanding! Exceeded expectations. Perfect for business events."
        ]
        
        for booking, escort in test_bookings:
            # Create rating from seeker to escort
            rating_value = random.randint(4, 5)  # Good ratings
            feedback = random.choice(sample_feedbacks)
            
            rating = Rating(
                booking_id=booking.id,
                reviewer_id=seeker.id,
                reviewed_id=escort.id,
                rating=rating_value,
                feedback=feedback,
                created_at=booking.end_time + timedelta(days=1)  # Rated next day
            )
            
            db.session.add(rating)
            print(f"✅ Created {rating_value}-star rating for {escort.email}")
        
        # Commit all changes
        db.session.commit()
        
        # Update profile ratings
        from controllers.rating_controller import RatingController
        for escort in escorts:
            RatingController.update_user_average_rating(escort.id)
        
        db.session.commit()
        
        print(f"\n🎉 Successfully created {len(test_bookings)} bookings and ratings!")
        
        # Verify creation
        total_bookings = Booking.query.count()
        total_ratings = Rating.query.count()
        print(f"📊 Total bookings in database: {total_bookings}")
        print(f"📊 Total ratings in database: {total_ratings}")
        
        return True

if __name__ == "__main__":
    try:
        create_test_ratings()
        print("\n✅ Test bookings and ratings created successfully!")
    except Exception as e:
        print(f"\n❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
