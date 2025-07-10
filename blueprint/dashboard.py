import os, requests, logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from blueprint.models import User, Profile, Favourite, Booking, Report
from extensions import db, limiter  # Import limiter for rate limiting
from blueprint.decorators import login_required
from blueprint.audit_log import log_event
from utils.utils import send_verification_email, verify_email_token, generate_otp, validate_phone_number, send_otp_sms, verify_otp_code, resend_otp, validate_password_strength, send_reset_email, verify_reset_token, consume_reset_token  # Import reset functions
from flask_wtf.csrf import generate_csrf  # Add this import
from utils.owasp_auth_security import OWASPAuthSecurity, progressive_delay_required  # OWASP Security

import boto3
from botocore.exceptions import ClientError
from flask import current_app

from blueprint.controller.dashboard_controller import DashboardController

# Configure security logging
# security_logger = logging.getLogger('security')
# security_logger.setLevel(logging.INFO)


# from blueprint.models import User, Profile
# auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def dashboard():
    role = session.get('role')
    user_id = session.get('user_id')
    data = {}
    
    # Initialize default values for all variables
    summary = None
    favourite_profiles = []

    if role == 'seeker':
        data['upcoming_bookings_count'] =DashboardController.get_upcoming_bookings_count(user_id)
        # data['upcoming_bookings_count'] = db.session.query(Booking).join(
        #     User, Booking.escort_id == User.id
        # ).filter(
        #     Booking.seeker_id == user_id,
        #     Booking.status == 'Confirmed',
        #     User.deleted == False,
        #     User.active == True,
        #     User.activate == True
        # ).count()

        # Fetch favourite escorts for this seeker
        # favourite_ids = [f.favourite_user_id for f in Favourite.query.filter_by(user_id=user_id).all()]
        favourite_ids = DashboardController.get_favourite_profiles(user_id)
        if favourite_ids:
            favourite_profiles = Profile.query.filter(Profile.user_id.in_(favourite_ids)).all()
        else:
            favourite_profiles = []
        summary = DashboardController.get_user_spending_summary(user_id)
        
    elif role == 'escort':
        data['booking_requests_count'] = DashboardController.get_booking_requests_count(user_id)
        # db.session.query(Booking).join(
        #     User, Booking.seeker_id == User.id
        # ).filter(
        #     Booking.escort_id == user_id,
        #     Booking.status == 'Pending',
        #     User.deleted == False,
        #     User.active == True,
        #     User.activate == True
        # ).count()
        
        # Fetch favourite seeker
        favourite_ids = [f.favourite_user_id for f in Favourite.query.filter_by(user_id=user_id).all()]
        if favourite_ids:
            favourite_profiles = Profile.query.filter(Profile.user_id.in_(favourite_ids)).all()
        else:
            favourite_profiles = []
        summary = DashboardController.get_user_earning_summary(user_id)
        
    elif role == 'admin':
        data['total_users'] = User.query.count()
        data['total_reports'] = Report.query.filter_by(
            status='Pending Review').count()
        data['seeker_to_escort_requests'] = User.query.filter(
            User.role == 'seeker',
            User.pending_role == 'escort'
        ).count()

        data['escort_to_seeker_requests'] = User.query.filter(
            User.role == 'escort',
            User.pending_role == 'seeker'
        ).count()
        
        # Admin doesn't need summary or favourite_profiles, but initialize them to avoid errors
        summary = None
        favourite_profiles = []

    return render_template('dashboard.html', role=role, data=data, summary=summary, favourite_profiles=favourite_profiles)


