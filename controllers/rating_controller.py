from flask import session, jsonify, request
from blueprint.models import db, User, Booking, Rating, Profile
from datetime import datetime


class RatingController:
    @staticmethod
    def can_rate_booking(booking_id, user_id):
        """Check if user can rate this booking"""
        booking = Booking.query.get(booking_id)
        if not booking:
            return False, "Booking not found"
        
        # Only participants can rate
        if user_id not in [booking.seeker_id, booking.escort_id]:
            return False, "Not authorized to rate this booking"
        
        # Booking must be completed
        if booking.status.lower() != 'completed':
            return False, "Can only rate completed bookings"
        
        # Check if already rated
        existing_rating = Rating.query.filter_by(
            booking_id=booking_id,
            reviewer_id=user_id
        ).first()
        if existing_rating:
            return False, "You have already rated this booking"
        
        return True, booking
    
    @staticmethod
    def submit_rating(booking_id, reviewer_id, rating_value, feedback=None):
        """Submit a rating for a booking"""
        try:
            # Start with a clean session
            try:
                db.session.rollback()  # Clear any previous state
            except:
                pass  # Ignore if no transaction to rollback
                
            # Validate rating
            if not (1 <= rating_value <= 5):
                return False, "Rating must be between 1 and 5"
            
            can_rate, result = RatingController.can_rate_booking(booking_id, reviewer_id)
            if not can_rate:
                return False, result
            
            booking = result
            
            # Check if this specific reviewer has already rated this booking
            existing_rating = Rating.query.filter_by(
                booking_id=booking_id,
                reviewer_id=reviewer_id
            ).first()
            
            if existing_rating:
                return False, "You have already rated this booking"
            
            # Determine who is being reviewed
            reviewed_id = booking.escort_id if reviewer_id == booking.seeker_id else booking.seeker_id
            
            # Create rating
            rating = Rating(
                booking_id=booking_id,
                reviewer_id=reviewer_id,
                reviewed_id=reviewed_id,
                rating=rating_value,
                feedback=feedback.strip() if feedback else None
            )
            
            db.session.add(rating)
            
            # Update user's average rating
            RatingController.update_user_average_rating(reviewed_id)
            
            db.session.commit()
            return True, rating
            
        except Exception as e:
            try:
                db.session.rollback()
            except:
                pass  # Ignore rollback errors
            return False, str(e)
    
    @staticmethod
    def update_user_average_rating(user_id):
        """Update a user's average rating in their profile"""
        try:
            # Calculate average rating
            ratings = Rating.query.filter_by(reviewed_id=user_id).all()
            if ratings:
                avg_rating = sum(r.rating for r in ratings) / len(ratings)
                avg_rating = round(avg_rating, 1)
                
                # Update profile
                profile = Profile.query.filter_by(user_id=user_id).first()
                if profile:
                    profile.rating = avg_rating
            
        except Exception as e:
            print(f"Error updating average rating: {e}")
    
    @staticmethod
    def get_user_ratings(user_id, limit=10):
        """Get ratings received by a user"""
        return Rating.query.filter_by(reviewed_id=user_id)\
                          .order_by(Rating.created_at.desc())\
                          .limit(limit).all()
    
    @staticmethod
    def get_booking_ratings(booking_id):
        """Get all ratings for a specific booking"""
        return Rating.query.filter_by(booking_id=booking_id).all()
    
    @staticmethod
    def get_rateable_bookings(user_id):
        """Get bookings that user can rate"""
        # Get completed bookings where user participated but hasn't rated yet
        completed_bookings = Booking.query.filter(
            ((Booking.seeker_id == user_id) | (Booking.escort_id == user_id)),
            db.func.lower(Booking.status) == 'completed'
        ).all()
        
        rateable = []
        for booking in completed_bookings:
            # Check if user has already rated this booking
            existing_rating = Rating.query.filter_by(
                booking_id=booking.id,
                reviewer_id=user_id
            ).first()
            
            if not existing_rating:
                rateable.append(booking)
        
        return rateable
    
    @staticmethod
    def get_rating_statistics(user_id):
        """Get rating statistics for a user"""
        ratings = Rating.query.filter_by(reviewed_id=user_id).all()
        
        if not ratings:
            return {
                'total_ratings': 0,
                'average_rating': 0,
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }
        
        total = len(ratings)
        average = sum(r.rating for r in ratings) / total
        
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in ratings:
            distribution[rating.rating] += 1
        
        return {
            'total_ratings': total,
            'average_rating': round(average, 1),
            'rating_distribution': distribution
        }
