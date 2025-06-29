
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from blueprint.models import Booking
from extensions import db
from blueprint.decorators import login_required


booking_bp = Blueprint('booking', __name__, url_prefix='/booking')


@booking_bp.route('/booking', methods=['GET', 'POST'])
@login_required
def booking():
    user_id = session['user_id']
    role = session['role']
    bookings_data = []

    if role == 'seeker':
        bookings_data = Booking.query.filter_by(seeker_id=user_id).order_by(Booking.booking_date.desc()).all()
    elif role == 'escort':
        bookings_data = Booking.query.filter_by(escort_id=user_id).order_by(Booking.booking_date.desc()).all()

    return render_template('booking.html', bookings=bookings_data, role=role)
