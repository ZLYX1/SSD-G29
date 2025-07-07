from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from blueprint.decorators import login_required
from controllers.rating_controller import RatingController
from blueprint.models import Booking, User, Profile, Rating

rating_bp = Blueprint('rating', __name__, url_prefix='/rating')

@rating_bp.route('/submit', methods=['POST'])
@login_required
def submit_rating():
    """Submit a rating via AJAX"""
    try:
        data = request.get_json()
        booking_id = data.get('booking_id')
        rating_value = data.get('rating')
        feedback = data.get('feedback', '')
        
        if not booking_id or not rating_value:
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        # Convert rating to int
        try:
            rating_value = int(rating_value)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Invalid rating value'})
        
        success, result = RatingController.submit_rating(
            booking_id=booking_id,
            reviewer_id=session['user_id'],
            rating_value=rating_value,
            feedback=feedback
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Rating submitted successfully',
                'rating_id': result.id
            })
        else:
            return jsonify({'success': False, 'error': result})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@rating_bp.route('/my-ratings')
@login_required
def my_ratings():
    """View user's received ratings"""
    user_id = session['user_id']
    ratings = RatingController.get_user_ratings(user_id)
    statistics = RatingController.get_rating_statistics(user_id)
    
    return render_template('ratings/my_ratings.html', 
                         ratings=ratings, 
                         statistics=statistics)

@rating_bp.route('/rateable-bookings')
@login_required
def rateable_bookings():
    """View bookings that can be rated"""
    user_id = session['user_id']
    bookings = RatingController.get_rateable_bookings(user_id)
    
    # Get additional info for each booking
    booking_data = []
    for booking in bookings:
        other_user_id = booking.escort_id if booking.seeker_id == user_id else booking.seeker_id
        other_user = User.query.get(other_user_id)
        other_profile = Profile.query.filter_by(user_id=other_user_id).first()
        
        booking_data.append({
            'booking': booking,
            'other_user': other_user,
            'other_profile': other_profile,
            'is_escort': booking.escort_id == other_user_id
        })
    
    return render_template('ratings/rateable_bookings.html', 
                         booking_data=booking_data)

@rating_bp.route('/user/<int:user_id>')
@login_required
def user_ratings(user_id):
    """View ratings for a specific user (public view)"""
    user = User.query.get_or_404(user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()
    ratings = RatingController.get_user_ratings(user_id, limit=20)
    statistics = RatingController.get_rating_statistics(user_id)
    
    return render_template('ratings/user_ratings.html',
                         user=user,
                         profile=profile,
                         ratings=ratings,
                         statistics=statistics)

@rating_bp.route('/booking/<int:booking_id>')
@login_required
def booking_ratings(booking_id):
    """View ratings for a specific booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user is authorized to view this booking
    user_id = session['user_id']
    if user_id not in [booking.seeker_id, booking.escort_id]:
        flash("You are not authorized to view this booking.", "danger")
        return redirect(url_for('dashboard'))
    
    ratings = RatingController.get_booking_ratings(booking_id)
    
    return render_template('ratings/booking_ratings.html',
                         booking=booking,
                         ratings=ratings)
