
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from blueprint.models import Booking, TimeSlot, User
from extensions import db
from blueprint.decorators import login_required
from datetime import datetime, timedelta
from flask_wtf.csrf import generate_csrf
import logging
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy.sql import func

from controllers.security_controller import SecurityController

booking_bp = Blueprint('booking', __name__, url_prefix='/booking')
logger = logging.getLogger(__name__)


def is_valid_datetime(dt_str):
    try:
        datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")
        return True
    except ValueError:
        return False


@booking_bp.route('/', methods=['GET', 'POST'])
@login_required
def booking():
    user_id = session['user_id']
    role = session['role']
    bookings_data = []
    time_slots = None

    if role == 'seeker':
        # Exclude bookings where the escort is deleted or banned
        bookings_data = Booking.query.join(User, Booking.escort_id == User.id).options(joinedload(Booking.payments)).filter(
            Booking.seeker_id == user_id,
            User.deleted == False,
            User.active == True  # Also exclude banned users
        ).order_by(Booking.start_time.desc()).all()
    elif role == 'escort':
        # Exclude bookings where the seeker is deleted or banned
        bookings_data = Booking.query.join(User, Booking.seeker_id == User.id).filter(
            Booking.escort_id == user_id,
            User.deleted == False,
            User.active == True  # Also exclude banned users
        ).order_by(Booking.start_time.desc()).all()
        time_slots = TimeSlot.query.filter(
            TimeSlot.user_id == user_id,
            TimeSlot.start_time >= datetime.utcnow()
        ).order_by(TimeSlot.start_time.asc()).all()

    return render_template('booking.html', bookings=bookings_data, time_slots=time_slots, role=role, csrf_token=generate_csrf())


@booking_bp.route('/slots/create', methods=['POST'])
@login_required
def create_slot():
    SecurityController.enforce_rbac('escort')
    SecurityController.check_csrf_token(request.form.get('csrf_token'))

    start_time_str = SecurityController.sanitize_input(request.form.get('start_time'))
    end_time_str = SecurityController.sanitize_input(request.form.get('end_time'))

    if not is_valid_datetime(start_time_str) or not is_valid_datetime(end_time_str):
        flash("Invalid datetime format.", "danger")
        return redirect(url_for('booking.booking'))

    start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")
    end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M")

    if start_time < datetime.utcnow():
        flash("Start time must be in the future.", "danger")
        return redirect(url_for('booking.booking'))

    if end_time <= start_time:
        flash("End time must be after start time.", "danger")
        return redirect(url_for('booking.booking'))

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
    logger.info(f"Escort {session['user_id']} created availability from {start_time} to {end_time}.")

    return redirect(url_for('booking.booking'))

def is_conflicting(user_id, requested_start, requested_end):
    # Query existing bookings for the escort
    existing = Booking.query.filter(
        Booking.escort_id == user_id,
        Booking.status == 'confirmed',  # or relevant status
        Booking.start_time < requested_end,
        Booking.end_time > requested_start
    ).first()
    return existing is not None


@booking_bp.route('/book/<int:escort_id>', methods=['POST'])
@login_required
def book(escort_id):
    seeker_id = session['user_id']

    slot_id = SecurityController.sanitize_input(request.form.get('slot_id'))
    requested_duration = request.form.get('duration', 15)
    requested_start_str = SecurityController.sanitize_input(request.form.get('start_time'))

    # Validate duration is integer and within allowed durations
    try:
        requested_duration = int(requested_duration)
        if requested_duration not in [15, 30, 45, 60]:
            raise ValueError("Invalid duration")
    except Exception:
        flash("Invalid duration selected.", "danger")
        return redirect(url_for('browse.view_profile', user_id=escort_id))

    # Validate the slot
    slot = TimeSlot.query.filter_by(id=slot_id, user_id=escort_id).first()
    if not slot:
        flash("Selected time slot is invalid.", "danger")
        return redirect(url_for('browse.view_profile', user_id=escort_id))

    if slot.end_time <= datetime.utcnow():
        flash("Selected time slot has already passed.", "danger")
        return redirect(url_for('browse.view_profile', user_id=escort_id))

    # Parse requested start time
    try:
        requested_start = datetime.strptime(requested_start_str, '%Y-%m-%d %H:%M')
    except Exception:
        flash("Invalid start time format.", "danger")
        return redirect(url_for('browse.view_profile', user_id=escort_id))

    # Calculate requested end time
    requested_end = requested_start + timedelta(minutes=requested_duration)

    # Check requested start/end boundaries inside slot
    if requested_start < slot.start_time or requested_end > slot.end_time:
        flash("Requested time is outside the available time slot.", "danger")
        return redirect(url_for('browse.view_profile', user_id=escort_id))

    # Check requested start is in future
    if requested_start < datetime.utcnow():
        flash("Requested start time is in the past.", "danger")
        return redirect(url_for('browse.view_profile', user_id=escort_id))

    # Check for conflicting escort bookings
    escort_conflict = Booking.query.join(User, Booking.seeker_id == User.id).filter(
        Booking.escort_id == escort_id,
        Booking.status.in_(["Pending", "Confirmed"]),
        Booking.start_time < requested_end,
        Booking.end_time > requested_start,
        User.deleted == False,
        User.active == True
    ).first()
    if escort_conflict:
        flash("This time overlaps with another booking for the escort.", "danger")
        return redirect(url_for('browse.view_profile', user_id=escort_id))

    # Check for conflicting seeker bookings
    seeker_conflict = Booking.query.join(User, Booking.escort_id == User.id).filter(
        Booking.seeker_id == seeker_id,
        Booking.status.in_(["Pending", "Confirmed"]),
        Booking.start_time < requested_end,
        Booking.end_time > requested_start,
        User.deleted == False,
        User.active == True
    ).first()
    if seeker_conflict:
        flash("You already have a booking that overlaps this time.", "danger")
        return redirect(url_for('browse.view_profile', user_id=escort_id))

    # Create the booking
    try:
        with db.session.begin_nested():
            new_booking = Booking(
                seeker_id=seeker_id,
                escort_id=escort_id,
                start_time=requested_start,
                end_time=requested_end,
                status='Pending'
            )
            db.session.add(new_booking)
        db.session.commit()
        flash("Booking request sent successfully.", "success")
        logger.info(f"Seeker {seeker_id} booked escort {escort_id} from {requested_start} to {requested_end}.")
    except Exception as e:
        db.session.rollback()
        flash(f"Booking failed: {e}", "danger")

    return redirect(url_for('browse.view_profile', user_id=escort_id))    # start_time_str = SecurityController.sanitize_input(request.form.get('start_time'))
    # duration_minutes = int(SecurityController.sanitize_input(request.form.get('duration')))

    # if not is_valid_datetime(start_time_str):
    #     flash("Invalid start time format.", "danger")
    #     return redirect(url_for('browse.view_profile', user_id=escort_id))

    # start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")
    # end_time = start_time + timedelta(minutes=duration_minutes)

    # if start_time < datetime.utcnow():
    #     flash("Booking start time must be in the future.", "danger")
    #     return redirect(url_for('browse.view_profile', user_id=escort_id))

    # available_slot = TimeSlot.query.filter(
    #     TimeSlot.user_id == escort_id,
    #     TimeSlot.start_time <= start_time,
    #     TimeSlot.end_time >= end_time
    # ).first()
    # if not available_slot:
    #     flash("Requested time is not within escort's available slots.", "danger")
    #     return redirect(url_for('browse.view_profile', user_id=escort_id))


    #     # Check overlapping bookings (confirmed or pending) for escort
    #     escort_overlap = Booking.query.join(User, Booking.seeker_id == User.id).filter(
    #         Booking.escort_id == escort_id,
    #         Booking.status.in_(["Pending", "Confirmed"]),
    #         Booking.start_time < end_time,
    #         Booking.end_time > start_time,
    #         User.deleted == False,  # Exclude bookings from deleted users
    #         User.active == True     # Exclude bookings from banned users
    #     ).first()
    #     if escort_overlap:
    #         flash("This time overlaps with an existing booking for the escort.", "danger")
    #         return redirect(url_for('browse.view_profile', user_id=escort_id))

    #     # Check overlapping bookings for seeker
    #     seeker_overlap = Booking.query.join(User, Booking.escort_id == User.id).filter(
    #         Booking.seeker_id == seeker_id,
    #         Booking.status.in_(["Pending", "Confirmed"]),
    #         Booking.start_time < end_time,
    #         Booking.end_time > start_time,
    #         User.deleted == False,  # Exclude bookings from deleted users
    #         User.active == True     # Exclude bookings from banned users
    #     ).first()
    #     if seeker_overlap:
    #         flash("You have another booking that overlaps with this time.", "danger")
    #         return redirect(url_for('browse.view_profile', user_id=escort_id))

    # try:
    #     with db.session.begin_nested():
    #         new_booking = Booking(
    #             seeker_id=seeker_id,
    #             escort_id=escort_id,
    #             start_time=start_time,
    #             end_time=end_time,
    #             status='Pending'
    #         )
    #         db.session.add(new_booking)
    #     db.session.commit()
    #     flash("Booking request sent.", "success")
    #     logger.info(f"Seeker {seeker_id} booked escort {escort_id} from {start_time} to {end_time}.")
    # except Exception as e:
    #     db.session.rollback()
    #     flash(f"Booking failed: {e}", "danger")

    # return redirect(url_for('browse.view_profile', user_id=escort_id))


@booking_bp.route('/handle', methods=['POST'])
@login_required
def handle_booking_action():
    SecurityController.enforce_rbac('escort')
    SecurityController.check_csrf_token(request.form.get('csrf_token'))

    booking_id = SecurityController.sanitize_input(request.form.get('booking_id'))
    action = SecurityController.sanitize_input(request.form.get('action'))

    booking = Booking.query.join(User, Booking.seeker_id == User.id).filter(
        Booking.id == booking_id,
        Booking.escort_id == session['user_id'],
        User.deleted == False,  # Exclude bookings from deleted users
        User.active == True     # Exclude bookings from banned users
    ).first()
    if not booking:
        flash("Booking not found, unauthorized, or user account is deleted/banned.", "danger")
        return redirect(url_for('booking.booking'))

    if action == 'accept':
        booking.status = 'Confirmed'
        flash(f"Booking #{booking.id} accepted.", "success")
        logger.info(f"Escort {session['user_id']} accepted booking #{booking.id}.")
    elif action == 'reject':
        booking.status = 'Rejected'
        flash(f"Booking #{booking.id} rejected.", "warning")
        logger.info(f"Escort {session['user_id']} rejected booking #{booking.id}.")
    else:
        flash("Invalid action.", "danger")
        return redirect(url_for('booking.booking'))

    db.session.commit()
    return redirect(url_for('booking.booking'))
