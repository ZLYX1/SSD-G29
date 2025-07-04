
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from blueprint.models import Booking, TimeSlot
from extensions import db
from blueprint.decorators import login_required
from datetime import datetime, timedelta

booking_bp = Blueprint('booking', __name__, url_prefix='/booking')


@booking_bp.route('/', methods=['GET', 'POST'])
@login_required
def booking():
    user_id = session['user_id']
    role = session['role']
    bookings_data = []
    time_slots = None  # default for non-escorts
    
    if role == 'seeker':
        bookings_data = Booking.query.filter_by(seeker_id=user_id).order_by(Booking.start_time.desc()).all()
    elif role == 'escort':
        bookings_data = Booking.query.filter_by(escort_id=user_id).order_by(Booking.start_time.desc()).all()
        time_slots = TimeSlot.query.filter(
            TimeSlot.user_id == user_id,
            TimeSlot.start_time >= datetime.utcnow()
        ).order_by(TimeSlot.start_time.asc()).all()


    return render_template('booking.html', bookings=bookings_data, time_slots=time_slots, role=role)

@booking_bp.route('/slots/create', methods=['POST'])
@login_required
def create_slot():
    role = session['role']
    if role != 'escort':
        flash("Only escorts can create availability slots.", "danger")
        return redirect(url_for('booking.booking'))

    start_time_str = request.form.get('start_time')  # e.g. '2025-07-01 13:00'
    end_time_str = request.form.get('end_time')      # e.g. '2025-07-01 19:00'

    try:
        # start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
        # end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M")

        # Add this check here:
        if start_time < datetime.utcnow():
            flash("Start time must be in the future.", "danger")
            return redirect(url_for('booking.booking'))
        
        if end_time <= start_time:
            flash("End time must be after start time.", "danger")
            return redirect(url_for('booking.booking'))

        # Optional: check overlapping time slots of same user to avoid duplicates
        # Check for overlapping slots for this escort
        overlapping_slot = TimeSlot.query.filter(
            TimeSlot.user_id == session['user_id'],
            TimeSlot.start_time < end_time,
            TimeSlot.end_time > start_time
        ).first()
        
        if overlapping_slot:
            flash("This availability slot overlaps with an existing slot.", "danger")
            return redirect(url_for('booking.booking'))

        new_slot = TimeSlot(user_id=session['user_id'], start_time=start_time, end_time=end_time)
        db.session.add(new_slot)
        db.session.commit()
        flash("Availability slot created.", "success")
    except Exception as e:
        flash(f"Error creating slot: {e}", "danger")

    return redirect(url_for('booking.booking'))

@booking_bp.route('/book/<int:escort_id>', methods=['POST'])
@login_required
def book(escort_id):
    seeker_id = session['user_id']
    start_time_str = request.form.get('start_time')  # e.g. '2025-07-01 14:15'
    duration_minutes = int(request.form.get('duration'))

    try:
        # start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Check if requested booking fits inside *any* availability slot for this escort
        if start_time < datetime.utcnow():
            flash("Booking start time must be in the future.", "danger")
            return redirect(url_for('browse.view_profile', user_id=escort_id))
        
        # Check if requested booking fits inside *any* availability slot for this escort
        available_slot = TimeSlot.query.filter(
            TimeSlot.user_id == escort_id,
            TimeSlot.start_time <= start_time,
            TimeSlot.end_time >= end_time
        ).first()
        if not available_slot:
            flash("Requested time is not within escort's available slots.", "danger")
            return redirect(url_for('browse.view_profile', user_id=escort_id))

        # Check overlapping bookings (confirmed or pending)
       # Check overlapping bookings (confirmed or pending) for escort
        escort_overlap = Booking.query.filter(
            Booking.escort_id == escort_id,
            Booking.status.in_(["Pending", "Confirmed"]),
            Booking.start_time < end_time,
            Booking.end_time > start_time
        ).first()
        if escort_overlap:
            flash("This time overlaps with an existing booking for the escort.", "danger")
            return redirect(url_for('browse.view_profile', user_id=escort_id))

        # Check overlapping bookings for seeker
        seeker_overlap = Booking.query.filter(
            Booking.seeker_id == seeker_id,
            Booking.status.in_(["Pending", "Confirmed"]),
            Booking.start_time < end_time,
            Booking.end_time > start_time
        ).first()
        if seeker_overlap:
            flash("You have another booking that overlaps with this time.", "danger")
            return redirect(url_for('browse.view_profile', user_id=escort_id))

        # Create booking
        new_booking = Booking(
            seeker_id=seeker_id,
            escort_id=escort_id,
            start_time=start_time,
            end_time=end_time,
            status='Pending'
        )
        db.session.add(new_booking)
        db.session.commit()
        flash("Booking request sent.", "success")
    except Exception as e:
        flash(f"Booking failed: {e}", "danger")

    return redirect(url_for('browse.view_profile', user_id=escort_id))


@booking_bp.route('/handle', methods=['POST'])
@login_required
def handle_booking_action():
    role = session.get('role')
    if role != 'escort':
        flash("Unauthorized action.", "danger")
        return redirect(url_for('booking.booking'))

    booking_id = request.form.get('booking_id')
    action = request.form.get('action')

    booking = Booking.query.get(booking_id)
    if not booking or booking.escort_id != session['user_id']:
        flash("Booking not found or unauthorized.", "danger")
        return redirect(url_for('booking.booking'))

    if action == 'accept':
        booking.status = 'Confirmed'
        flash(f"Booking #{booking.id} accepted.", "success")
    elif action == 'reject':
        booking.status = 'Rejected'
        flash(f"Booking #{booking.id} rejected.", "warning")
    else:
        flash("Invalid action.", "danger")
        return redirect(url_for('booking.booking'))

    db.session.commit()
    return redirect(url_for('booking.booking'))
