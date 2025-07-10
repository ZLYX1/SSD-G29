/*
Do not touch this file!! To be used for refactoring purpsoes
*/

// // boundary/dashboard.py

// from flask import Blueprint, session, render_template
// from blueprint.decorators import login_required
// from models import Booking, User, Favourite, Profile, Report
// from controllers.dashboard_controller import DashboardController

// bp = Blueprint('dashboard', __name__)

// @bp.route('/dashboard')
// @login_required
// def dashboard():
//     role = session.get('role')
//     user_id = session.get('user_id')
//     data = {}

//     if role == 'seeker':
//         data['upcoming_bookings_count'] = Booking.query.join(
//             User, Booking.escort_id == User.id
//         ).filter(
//             Booking.seeker_id == user_id,
//             Booking.status == 'Confirmed',
//             User.deleted == False,
//             User.active == True,
//             User.activate == True
//         ).count()

//         favourite_ids = [f.favourite_user_id for f in Favourite.query.filter_by(user_id=user_id).all()]
//         favourite_profiles = Profile.query.filter(Profile.user_id.in_(favourite_ids)).all() if favourite_ids else []

//         summary = DashboardController.get_user_spending_summary(user_id)

//     elif role == 'escort':
//         data['booking_requests_count'] = Booking.query.join(
//             User, Booking.seeker_id == User.id
//         ).filter(
//             Booking.escort_id == user_id,
//             Booking.status == 'Pending',
//             User.deleted == False,
//             User.active == True,
//             User.activate == True
//         ).count()

//         favourite_ids = [f.favourite_user_id for f in Favourite.query.filter_by(user_id=user_id).all()]
//         favourite_profiles = Profile.query.filter(Profile.user_id.in_(favourite_ids)).all() if favourite_ids else []

//         summary = DashboardController.get_user_earning_summary(user_id)

//     elif role == 'admin':
//         data['total_users'] = User.query.count()
//         data['total_reports'] = Report.query.filter_by(status='Pending Review').count()
//         data['seeker_to_escort_requests'] = User.query.filter(User.role == 'seeker', User.pending_role == 'escort').count()
//         data['escort_to_seeker_requests'] = User.query.filter(User.role == 'escort', User.pending_role == 'seeker').count()
//         favourite_profiles = []
//         summary = {}

//     return render_template('dashboard.html', role=role, data=data, summary=summary, favourite_profiles=favourite_profiles)

// // # controllers/rating_controller.py
// // Controller for handling ratings: submission, statistics, filtering rateable bookings, and retrieving ratings.
// from models import Rating, Booking, User
// from extensions import db
// from sqlalchemy import func

// class RatingController:
//     @staticmethod
//     def submit_rating(booking_id, reviewer_id, rating_value, feedback):
//         booking = Booking.query.get(booking_id)
//         if not booking or (reviewer_id not in [booking.seeker_id, booking.escort_id]):
//             return False, "Invalid booking or unauthorized reviewer."

//         existing_rating = Rating.query.filter_by(booking_id=booking_id, reviewer_id=reviewer_id).first()
//         if existing_rating:
//             return False, "You have already rated this booking."

//         recipient_id = booking.escort_id if reviewer_id == booking.seeker_id else booking.seeker_id

//         new_rating = Rating(
//             booking_id=booking_id,
//             reviewer_id=reviewer_id,
//             recipient_id=recipient_id,
//             rating=rating_value,
//             feedback=feedback
//         )
//         db.session.add(new_rating)
//         db.session.commit()
//         return True, new_rating

//     @staticmethod
//     def get_user_ratings(user_id, limit=None):
//         query = Rating.query.filter_by(recipient_id=user_id).order_by(Rating.created_at.desc())
//         if limit:
//             query = query.limit(limit)
//         return query.all()

//     @staticmethod
//     def get_user_given_ratings(user_id):
//         return Rating.query.filter_by(reviewer_id=user_id).order_by(Rating.created_at.desc()).all()

//     @staticmethod
//     def get_booking_ratings(booking_id):
//         return Rating.query.filter_by(booking_id=booking_id).all()

//     @staticmethod
//     def get_rating_statistics(user_id):
//         ratings = Rating.query.filter_by(recipient_id=user_id).all()
//         if not ratings:
//             return {"average": 0, "count": 0}

//         total = sum(r.rating for r in ratings)
//         count = len(ratings)
//         return {
//             "average": round(total / count, 2),
//             "count": count
//         }

//     @staticmethod
//     def get_rateable_bookings(user_id):
//         bookings = Booking.query.filter(
//             (Booking.seeker_id == user_id) | (Booking.escort_id == user_id),
//             Booking.status == 'Completed'
//         ).all()

//         rateable = []
//         for b in bookings:
//             existing_rating = Rating.query.filter_by(booking_id=b.id, reviewer_id=user_id).first()
//             if not existing_rating:
//                 rateable.append(b)
//         return rateable

// /* or */
// controllers/rating_controller.py
// from blueprint.models import Rating, Booking
// from extensions import db

// class RatingController:

//     @staticmethod
//     def submit_rating(booking_id, reviewer_id, rating_value, feedback=''):
//         # Check if rating exists for booking + reviewer
//         existing = Rating.query.filter_by(booking_id=booking_id, reviewer_id=reviewer_id).first()
//         if existing:
//             return False, "You have already rated this booking."

//         # Create rating
//         new_rating = Rating(
//             booking_id=booking_id,
//             reviewer_id=reviewer_id,
//             rating=rating_value,
//             feedback=feedback
//         )
//         db.session.add(new_rating)
//         db.session.commit()
//         return True, new_rating

//     @staticmethod
//     def get_user_ratings(user_id, limit=None):
//         query = Rating.query.filter_by(reviewee_id=user_id).order_by(Rating.created_at.desc())
//         if limit:
//             query = query.limit(limit)
//         return query.all()

//     @staticmethod
//     def get_user_given_ratings(user_id):
//         return Rating.query.filter_by(reviewer_id=user_id).order_by(Rating.created_at.desc()).all()

//     @staticmethod
//     def get_rating_statistics(user_id):
//         from sqlalchemy import func
//         avg_rating = db.session.query(func.avg(Rating.rating)).filter_by(reviewee_id=user_id).scalar() or 0
//         count = db.session.query(func.count(Rating.id)).filter_by(reviewee_id=user_id).scalar() or 0
//         return {"average_rating": round(avg_rating, 2), "count": count}

//     @staticmethod
//     def get_rateable_bookings(user_id):
//         # Bookings user can rate (e.g. completed bookings without rating)
//         # Simplified example: bookings with status 'Completed' and not yet rated by user
//         rated_booking_ids = [r.booking_id for r in Rating.query.filter_by(reviewer_id=user_id).all()]
//         bookings = Booking.query.filter(
//             ((Booking.seeker_id == user_id) | (Booking.escort_id == user_id)),
//             Booking.status == 'Completed',
//             ~Booking.id.in_(rated_booking_ids)
//         ).all()
//         return bookings

//     @staticmethod
//     def get_booking_ratings(booking_id):
//         return Rating.query.filter_by(booking_id=booking_id).all()

// // controllers/report_controller.py
// from blueprint.models import Report
// from extensions import db
// import json

// class ReportController:

//     @staticmethod
//     def create_report(reporter_id, reported_id, report_type, title, description, evidence_urls=None, severity='Medium'):
//         try:
//             evidence_json = json.dumps(evidence_urls) if evidence_urls else None
//             report = Report(
//                 reporter_id=reporter_id,
//                 reported_id=reported_id,
//                 report_type=report_type,
//                 title=title,
//                 description=description,
//                 evidence_urls=evidence_json,
//                 severity=severity,
//                 status='Pending Review'
//             )
//             db.session.add(report)
//             db.session.commit()
//             return {'success': True, 'message': 'Report submitted successfully.'}
//         except Exception as e:
//             db.session.rollback()
//             return {'success': False, 'message': f'Failed to submit report: {str(e)}'}

//     @staticmethod
//     def get_report_types():
//         # Example static list; replace with DB if dynamic
//         return ['Spam', 'Harassment', 'Inappropriate Content', 'Other']

//     @staticmethod
//     def get_severity_levels():
//         return ['Low', 'Medium', 'High', 'Critical']

//     @staticmethod
//     def get_user_reports(user_id, mode='made'):
//         if mode == 'made':
//             return Report.query.filter_by(reporter_id=user_id).order_by(Report.created_at.desc()).all()
//         elif mode == 'received':
//             return Report.query.filter_by(reported_id=user_id).order_by(Report.created_at.desc()).all()
//         return []

//     @staticmethod
//     def get_all_reports(status_filter=None, severity_filter=None):
//         query = Report.query
//         if status_filter:
//             query = query.filter_by(status=status_filter)
//         if severity_filter:
//             query = query.filter_by(severity=severity_filter)
//         return query.order_by(Report.created_at.desc()).all()

//     @staticmethod
//     def update_report_status(report_id, new_status, admin_id, admin_notes=None, resolution=None):
//         report = Report.query.get(report_id)
//         if not report:
//             return {'success': False, 'message': 'Report not found'}
//         report.status = new_status
//         report.admin_notes = admin_notes
//         report.resolution = resolution
//         report.admin_id = admin_id
//         try:
//             db.session.commit()
//             return {'success': True, 'message': 'Report status updated'}
//         except Exception as e:
//             db.session.rollback()
//             return {'success': False, 'message': f'Error updating report: {str(e)}'}

//     @staticmethod
//     def get_report_statistics():
//         # You can customize the statistics returned here
//         from sqlalchemy import func
//         total_reports = Report.query.count()
//         pending_reports = Report.query.filter_by(status='Pending Review').count()
//         resolved_reports = Report.query.filter(Report.status.in_(['Resolved', 'Closed'])).count()
//         return {
//             'total_reports': total_reports,
//             'pending_reports': pending_reports,
//             'resolved_reports': resolved_reports
//         }

//     @staticmethod
//     def search_reports(search_term, search_type='all'):
//         # Simplified example: search by title or description
//         from sqlalchemy import or_
//         query = Report.query
//         if search_type == 'title':
//             query = query.filter(Report.title.ilike(f'%{search_term}%'))
//         elif search_type == 'description':
//             query = query.filter(Report.description.ilike(f'%{search_term}%'))
//         else:
//             query = query.filter(or_(
//                 Report.title.ilike(f'%{search_term}%'),
//                 Report.description.ilike(f'%{search_term}%')
//             ))
//         return query.order_by(Report.created_at.desc()).all()

// // controllers/profile_controller.py
// # controllers/profile_controller.py
// # Controller for profile-related business logic

// from blueprint.models import Profile, User, db

// class ProfileController:
//     @staticmethod
//     def get_profile_by_user_id(user_id):
//         return Profile.query.filter_by(user_id=user_id).first()

//     @staticmethod
//     def update_profile(user_id, name=None, bio=None, availability=None, photo=None):
//         profile = Profile.query.filter_by(user_id=user_id).first()
//         if not profile:
//             return None, "Profile not found"

//         if name is not None:
//             profile.name = name
//         if bio is not None:
//             profile.bio = bio
//         if availability is not None:
//             profile.availability = availability
//         if photo is not None:
//             profile.photo = photo

//         db.session.commit()
//         return profile, None

//     @staticmethod
//     def save_photo_url(user_id, photo_url):
//         profile = Profile.query.filter_by(user_id=user_id).first()
//         if not profile:
//             return None, "Profile not found"
//         profile.photo = photo_url
//         db.session.commit()
//         return profile, None

//     @staticmethod
//     def request_role_change(user):
//         if user.role == 'seeker':
//             user.pending_role = 'escort'
//         elif user.role == 'escort':
//             user.pending_role = 'seeker'
//         else:
//             return False, "Role change not allowed"
//         db.session.commit()
//         return True, None

//     @staticmethod
//     def deactivate_user(user):
//         user.activate = False
//         db.session.commit()
//         return True

// /* or */
// #controllers/profile_controller.py
// from blueprint.models import Profile, User
// from extensions import db

// class ProfileController:

//     @staticmethod
//     def get_profile_by_user_id(user_id):
//         return Profile.query.filter_by(user_id=user_id).first()

//     @staticmethod
//     def update_profile(user_id, name=None, bio=None, availability=None, photo_url=None):
//         profile = Profile.query.filter_by(user_id=user_id).first()
//         if not profile:
//             return False, "Profile not found"
//         if name is not None:
//             profile.name = name
//         if bio is not None:
//             profile.bio = bio
//         if availability is not None:
//             profile.availability = availability
//         if photo_url:
//             profile.photo = photo_url
//         db.session.commit()
//         return True, "Profile updated"

//     @staticmethod
//     def request_role_change(user):
//         if user.role == 'seeker':
//             user.pending_role = 'escort'
//         elif user.role == 'escort':
//             user.pending_role = 'seeker'
//         else:
//             return False, "Role change not allowed"
//         db.session.commit()
//         return True, "Role change requested"

//     @staticmethod
//     def deactivate_user(user):
//         user.activate = False
//         db.session.commit()
//         return True

// boundary/profile.py
// # boundary/profile.py
// # Boundary for handling profile-related HTTP requests and responses

// from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
// from blueprint.decorators import login_required
// from controllers.profile_controller import ProfileController
// from blueprint.models import User

// profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

// @profile_bp.route('/', methods=['GET', 'POST'])
// @login_required
// def profile():
//     user_id = session['user_id']
//     profile = ProfileController.get_profile_by_user_id(user_id)

//     if request.method == 'POST':
//         name = request.form.get('name')
//         bio = request.form.get('bio')
//         availability = request.form.get('availability')
//         photo_url = request.form.get('photo_url')

//         updated_profile, error = ProfileController.update_profile(
//             user_id, name=name, bio=bio, availability=availability, photo=photo_url
//         )
//         if error:
//             flash(error, 'danger')
//         else:
//             flash("Profile updated successfully!", "success")
//             return redirect(url_for('profile.profile'))

//     return render_template('profile.html', profile=profile)

// @profile_bp.route('/photo', methods=['GET'])
// @login_required
// def get_profile_photo():
//     user_id = session.get('user_id')
//     profile = ProfileController.get_profile_by_user_id(user_id)
//     if not profile:
//         return jsonify({'error': 'Profile not found'}), 404
//     return jsonify({'user_id': user_id, 'photo_url': profile.photo or 'https://via.placeholder.com/150'})

// @profile_bp.route('/save-photo', methods=['POST'])
// @login_required
// def save_photo():
//     data = request.get_json()
//     photo_url = data.get('photo_url')
//     if not photo_url:
//         return jsonify({'error': 'Missing photo URL'}), 400

//     user_id = session['user_id']
//     profile, error = ProfileController.save_photo_url(user_id, photo_url)
//     if error:
//         return jsonify({'error': error}), 404
//     return jsonify({'message': 'Photo saved successfully'}), 200

// @profile_bp.route('/request-role-change', methods=['POST'])
// @login_required
// def request_role_change():
//     user_id = session['user_id']
//     user = User.query.get(user_id)
//     success, error = ProfileController.request_role_change(user)
//     if not success:
//         flash(error, 'warning')
//     else:
//         flash("Role change request submitted. Awaiting admin approval.", "info")
//     return redirect(url_for('profile.profile'))

// @profile_bp.route('/deactivate', methods=['POST'])
// @login_required
// def deactivate_profile():
//     user_id = session['user_id']
//     user = User.query.get(user_id)
//     if not user:
//         flash("User not found.", "danger")
//         return redirect(url_for('profile.profile'))
//     ProfileController.deactivate_user(user)
//     session.clear()
//     flash("Your account has been deactivated. You are now logged out.", "info")
//     return redirect(url_for('auth.auth', mode='login'))

// controllers/booking_controller.py
// # controllers/booking_controller.py
// # Controller for booking business logic

// from blueprint.models import Booking, User, db

// class BookingController:
//     @staticmethod
//     def get_bookings_for_user(user_id, role='seeker', status=None):
//         query = Booking.query
//         if role == 'seeker':
//             query = query.filter_by(seeker_id=user_id)
//         elif role == 'escort':
//             query = query.filter_by(escort_id=user_id)

//         if status:
//             query = query.filter_by(status=status)

//         return query.all()

//     @staticmethod
//     def create_booking(seeker_id, escort_id, start_time, end_time, status='Pending'):
//         booking = Booking(
//             seeker_id=seeker_id,
//             escort_id=escort_id,
//             start_time=start_time,
//             end_time=end_time,
//             status=status
//         )
//         db.session.add(booking)
//         db.session.commit()
//         return booking

//     @staticmethod
//     def update_booking_status(booking_id, status):
//         booking = Booking.query.get(booking_id)
//         if not booking:
//             return False, "Booking not found"
//         booking.status = status
//         db.session.commit()
//         return True, None

//     @staticmethod
//     def delete_booking(booking_id):
//         booking = Booking.query.get(booking_id)
//         if not booking:
//             return False, "Booking not found"
//         db.session.delete(booking)
//         db.session.commit()
//         return True, None
// '

// boundary/booking.py
// # boundary/booking.py
// # Boundary for booking-related HTTP routes

// from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
// from blueprint.decorators import login_required
// from controllers.booking_controller import BookingController

// booking_bp = Blueprint('booking', __name__, url_prefix='/booking')

// @booking_bp.route('/my-bookings')
// @login_required
// def my_bookings():
//     user_id = session['user_id']
//     role = session['role']
//     bookings = BookingController.get_bookings_for_user(user_id, role)
//     return render_template('booking/my_bookings.html', bookings=bookings)

// @booking_bp.route('/create', methods=['GET', 'POST'])
// @login_required
// def create_booking():
//     if request.method == 'POST':
//         seeker_id = session['user_id']
//         escort_id = request.form.get('escort_id')
//         start_time = request.form.get('start_time')
//         end_time = request.form.get('end_time')
//         # You might want to parse datetime strings here

//         booking = BookingController.create_booking(seeker_id, escort_id, start_time, end_time)
//         flash("Booking created successfully", "success")
//         return redirect(url_for('booking.my_bookings'))

//     # For GET, show a booking creation form
//     return render_template('booking/create_booking.html')

// @booking_bp.route('/update-status/<int:booking_id>', methods=['POST'])
// @login_required
// def update_booking_status(booking_id):
//     status = request.form.get('status')
//     success, error = BookingController.update_booking_status(booking_id, status)
//     if success:
//         flash("Booking status updated", "success")
//     else:
//         flash(error or "Failed to update booking status", "danger")
//     return redirect(url_for('booking.my_bookings'))

// @booking_bp.route('/delete/<int:booking_id>', methods=['POST'])
// @login_required
// def delete_booking(booking_id):
//     success, error = BookingController.delete_booking(booking_id)
//     if success:
//         flash("Booking deleted", "success")
//     else:
//         flash(error or "Failed to delete booking", "danger")
//     return redirect(url_for('booking.my_bookings'))

// controllers/payment_controller.py
// # controllers/payment_controller.py
// # Controller for payment business logic

// from blueprint.models import Payment, Booking, db
// from sqlalchemy import func, text

// class PaymentController:
//     @staticmethod
//     def get_user_spending_summary(user_id):
//         if not user_id:
//             return None

//         total_spent = db.session.query(func.sum(Payment.amount)).filter_by(user_id=user_id).scalar() or 0
//         total_transactions = db.session.query(func.count(Payment.id)).filter_by(user_id=user_id).scalar()

//         monthly_breakdown = db.session.query(
//             func.date_trunc('month', Payment.created_at).label('month'),
//             func.sum(Payment.amount).label('total')
//         ).filter(
//             Payment.user_id == user_id
//         ).group_by(
//             func.date_trunc('month', Payment.created_at)
//         ).order_by(text('month desc')).limit(6).all()

//         breakdown = [{"month": month.strftime("%Y-%m"), "total": float(total)} for month, total in monthly_breakdown]

//         return {
//             "total_spent": round(float(total_spent), 2),
//             "transaction_count": total_transactions,
//             "monthly_breakdown": breakdown
//         }

//     @staticmethod
//     def get_user_earning_summary(user_id):
//         if not user_id:
//             return None

//         total_earned = db.session.query(func.sum(Payment.amount)).join(
//             Booking, Payment.booking_id == Booking.id
//         ).filter(Booking.escort_id == user_id).scalar() or 0

//         total_paid_bookings = db.session.query(func.count(Payment.id)).join(
//             Booking, Payment.booking_id == Booking.id
//         ).filter(Booking.escort_id == user_id).scalar()

//         monthly_earnings = db.session.query(
//             func.date_trunc('month', Payment.created_at).label('month'),
//             func.sum(Payment.amount).label('total')
//         ).join(
//             Booking, Payment.booking_id == Booking.id
//         ).filter(
//             Booking.escort_id == user_id
//         ).group_by(
//             func.date_trunc('month', Payment.created_at)
//         ).order_by(text('month desc')).limit(6).all()

//         breakdown = [{"month": month.strftime("%Y-%m"), "total": float(total)} for month, total in monthly_earnings]

//         return {
//             "total_earned": round(float(total_earned), 2),
//             "paid_bookings": total_paid_bookings,
//             "monthly_breakdown": breakdown
//         }

// boundary/payment.py

// # boundary/payment.py
// # Boundary for payment-related routes

// from flask import Blueprint, render_template, session
// from blueprint.decorators import login_required
// from controllers.payment_controller import PaymentController

// payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

// @payment_bp.route('/summary')
// @login_required
// def payment_summary():
//     user_id = session['user_id']
//     role = session['role']
//     summary = None

//     if role == 'seeker':
//         summary = PaymentController.get_user_spending_summary(user_id)
//     elif role == 'escort':
//         summary = PaymentController.get_user_earning_summary(user_id)

//     return render_template('payment/summary.html', summary=summary)

// // boundary/auth.py
// from flask import Blueprint, request, render_template, flash, redirect, url_for, session
// from controllers.auth_controller import AuthController
// from blueprint.decorators import login_required

// auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

// @auth_bp.route('/login', methods=['GET', 'POST'])
// def login():
//     if request.method == 'POST':
//         email = request.form.get('email')
//         password = request.form.get('password')
//         if AuthController.authenticate(email, password):
//             session.clear()
//             session['user_id'] = User.query.filter_by(email=email).first().id
//             session['role'] = User.query.filter_by(email=email).first().role
//             flash('Login successful', 'success')
//             return redirect(url_for('dashboard'))
//         else:
//             flash('Invalid email or password', 'danger')
//     return render_template('auth/login.html')

// @auth_bp.route('/logout')
// @login_required
// def logout():
//     session.clear()
//     flash('You have been logged out.', 'success')
//     return redirect(url_for('auth.login'))

// @auth_bp.route('/register', methods=['GET', 'POST'])
// def register():
//     if request.method == 'POST':
//         email = request.form.get('email')
//         password = request.form.get('password')
//         confirm_password = request.form.get('confirm_password')

//         if password != confirm_password:
//             flash("Passwords do not match", "danger")
//             return render_template('auth/register.html')

//         if AuthController.register(email, password):
//             flash('Account created successfully. Please log in.', 'success')
//             return redirect(url_for('auth.login'))
//         else:
//             flash('Email already registered', 'danger')
//     return render_template('auth/register.html')

// // controllers/rating_controller.py
// from blueprint.models import Rating, Booking, db
// from sqlalchemy import and_

// class RatingController:
//     @staticmethod
//     def submit_rating(booking_id, reviewer_id, rating_value, feedback):
//         # Check if booking exists and reviewer is part of it
//         booking = Booking.query.get(booking_id)
//         if not booking:
//             return False, "Booking not found."
//         if reviewer_id not in [booking.seeker_id, booking.escort_id]:
//             return False, "You are not authorized to rate this booking."

//         # Prevent duplicate ratings for same booking by same reviewer
//         existing = Rating.query.filter_by(booking_id=booking_id, reviewer_id=reviewer_id).first()
//         if existing:
//             return False, "You have already rated this booking."

//         rating = Rating(
//             booking_id=booking_id,
//             reviewer_id=reviewer_id,
//             rating_value=rating_value,
//             feedback=feedback
//         )
//         db.session.add(rating)
//         db.session.commit()
//         return True, rating

//     @staticmethod
//     def get_user_ratings(user_id, limit=None):
//         # Ratings received by user (as either seeker or escort)
//         query = Rating.query.join(Booking).filter(
//             (Booking.seeker_id == user_id) | (Booking.escort_id == user_id)
//         ).order_by(Rating.created_at.desc())

//         if limit:
//             query = query.limit(limit)
//         return query.all()

//     @staticmethod
//     def get_user_given_ratings(user_id):
//         # Ratings the user has given
//         return Rating.query.filter_by(reviewer_id=user_id).order_by(Rating.created_at.desc()).all()

//     @staticmethod
//     def get_rating_statistics(user_id):
//         # Calculate average rating and count for user
//         from sqlalchemy import func
//         ratings = Rating.query.join(Booking).filter(
//             (Booking.seeker_id == user_id) | (Booking.escort_id == user_id)
//         )
//         avg_rating = ratings.with_entities(func.avg(Rating.rating_value)).scalar() or 0
//         count = ratings.count()
//         return {"average": round(avg_rating, 2), "count": count}

//     @staticmethod
//     def get_rateable_bookings(user_id):
//         # Bookings user is part of, completed, but not yet rated by user
//         rated_booking_ids = [r.booking_id for r in Rating.query.filter_by(reviewer_id=user_id).all()]
//         bookings = Booking.query.filter(
//             ((Booking.seeker_id == user_id) | (Booking.escort_id == user_id)),
//             Booking.status == 'Completed',
//             ~Booking.id.in_(rated_booking_ids)
//         ).all()
//         return bookings

//     @staticmethod
//     def get_booking_ratings(booking_id):
//         return Rating.query.filter_by(booking_id=booking_id).all()

// // boundary/rating.py
// from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
// from blueprint.decorators import login_required
// from controllers.rating_controller import RatingController
// from blueprint.models import User, Profile, Booking

// rating_bp = Blueprint('rating', __name__, url_prefix='/rating')

// @rating_bp.route('/submit', methods=['POST'])
// @login_required
// def submit_rating():
//     data = request.get_json()
//     booking_id = data.get('booking_id')
//     rating_value = data.get('rating')
//     feedback = data.get('feedback', '')

//     if not booking_id or not rating_value:
//         return jsonify({'success': False, 'error': 'Missing required fields'})

//     try:
//         rating_value = int(rating_value)
//     except:
//         return jsonify({'success': False, 'error': 'Invalid rating value'})

//     success, result = RatingController.submit_rating(booking_id, session['user_id'], rating_value, feedback)

//     if success:
//         return jsonify({'success': True, 'message': 'Rating submitted successfully', 'rating_id': result.id})
//     else:
//         return jsonify({'success': False, 'error': result})

// @rating_bp.route('/my-ratings')
// @login_required
// def my_ratings():
//     user_id = session['user_id']
//     user = User.query.get(user_id)
//     ratings_received = RatingController.get_user_ratings(user_id)
//     ratings_given = RatingController.get_user_given_ratings(user_id)
//     statistics = RatingController.get_rating_statistics(user_id)
//     return render_template('ratings/my_ratings.html',
//                            ratings_received=ratings_received,
//                            ratings_given=ratings_given,
//                            statistics=statistics,
//                            user=user)

// @rating_bp.route('/rateable-bookings')
// @login_required
// def rateable_bookings():
//     user_id = session['user_id']
//     bookings = RatingController.get_rateable_bookings(user_id)

//     booking_data = []
//     for booking in bookings:
//         other_user_id = booking.escort_id if booking.seeker_id == user_id else booking.seeker_id
//         other_user = User.query.get(other_user_id)
//         other_profile = Profile.query.filter_by(user_id=other_user_id).first()
//         booking_data.append({
//             'booking': booking,
//             'other_user': other_user,
//             'other_profile': other_profile,
//             'is_escort': booking.escort_id == other_user_id
//         })

//     return render_template('ratings/rateable_bookings.html', booking_data=booking_data)

// @rating_bp.route('/user/<int:user_id>')
// @login_required
// def user_ratings(user_id):
//     user = User.query.get_or_404(user_id)
//     profile = Profile.query.filter_by(user_id=user_id).first()
//     ratings = RatingController.get_user_ratings(user_id, limit=20)
//     statistics = RatingController.get_rating_statistics(user_id)
//     return render_template('ratings/user_ratings.html',
//                            user=user,
//                            profile=profile,
//                            ratings=ratings,
//                            statistics=statistics)

// @rating_bp.route('/booking/<int:booking_id>')
// @login_required
// def booking_ratings(booking_id):
//     booking = Booking.query.get_or_404(booking_id)
//     user_id = session['user_id']
//     if user_id not in [booking.seeker_id, booking.escort_id]:
//         flash("You are not authorized to view this booking.", "danger")
//         return redirect(url_for('dashboard'))
//     ratings = RatingController.get_booking_ratings(booking_id)
//     return render_template('ratings/booking_ratings.html', booking=booking, ratings=ratings)

// controllers/report_controller.py
// from blueprint.models import Report, db
// from datetime import datetime

// class ReportController:
//     @staticmethod
//     def create_report(reporter_id, reported_id, report_type, title, description, evidence_urls=None, severity='Medium'):
//         try:
//             if evidence_urls and isinstance(evidence_urls, list):
//                 import json
//                 evidence_urls = json.dumps(evidence_urls)
//             new_report = Report(
//                 reporter_id=reporter_id,
//                 reported_id=reported_id,
//                 report_type=report_type,
//                 title=title,
//                 description=description,
//                 evidence_urls=evidence_urls,
//                 severity=severity,
//                 status='Pending Review',
//                 created_at=datetime.utcnow()
//             )
//             db.session.add(new_report)
//             db.session.commit()
//             return {'success': True, 'message': 'Report submitted successfully.'}
//         except Exception as e:
//             return {'success': False, 'message': f'Error submitting report: {str(e)}'}

//     @staticmethod
//     def get_user_reports(user_id, report_direction='made'):
//         if report_direction == 'made':
//             return Report.query.filter_by(reporter_id=user_id).order_by(Report.created_at.desc()).all()
//         elif report_direction == 'received':
//             return Report.query.filter_by(reported_id=user_id).order_by(Report.created_at.desc()).all()
//         else:
//             return []

//     @staticmethod
//     def get_report_types():
//         # Return list of report types - can be static or from DB
//         return ['Spam', 'Harassment', 'Inappropriate Content', 'Fraud', 'Other']

//     @staticmethod
//     def get_severity_levels():
//         return ['Low', 'Medium', 'High', 'Critical']

//     @staticmethod
//     def get_all_reports(status=None, severity=None):
//         query = Report.query
//         if status:
//             query = query.filter_by(status=status)
//         if severity:
//             query = query.filter_by(severity=severity)
//         return query.order_by(Report.created_at.desc()).all()

//     @staticmethod
//     def search_reports(term, search_type='all'):
//         term = f'%{term}%'
//         query = Report.query
//         if search_type == 'title':
//             query = query.filter(Report.title.ilike(term))
//         elif search_type == 'description':
//             query = query.filter(Report.description.ilike(term))
//         elif search_type == 'reporter':
//             query = query.join('reporter').filter(Report.reporter.has(email=term))
//         else:  # all
//             query = query.filter(
//                 (Report.title.ilike(term)) |
//                 (Report.description.ilike(term))
//             )
//         return query.order_by(Report.created_at.desc()).all()

//     @staticmethod
//     def update_report_status(report_id, new_status, admin_id, admin_notes=None, resolution=None):
//         report = Report.query.get(report_id)
//         if not report:
//             return {'success': False, 'message': 'Report not found.'}
//         report.status = new_status
//         report.admin_notes = admin_notes
//         report.resolution = resolution
//         report.reviewed_by_admin_id = admin_id
//         report.reviewed_at = datetime.utcnow()
//         db.session.commit()
//         return {'success': True, 'message': 'Report status updated successfully.'}

//     @staticmethod
//     def get_report_statistics():
//         # Example statistics: counts by status and severity
//         from sqlalchemy import func
//         stats = {
//             'by_status': db.session.query(Report.status, func.count(Report.id)).group_by(Report.status).all(),
//             'by_severity': db.session.query(Report.severity, func.count(Report.id)).group_by(Report.severity).all(),
//             'total_reports': Report.query.count()
//         }
//         return stats

// // boundary/report.py
// from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
// from blueprint.decorators import login_required, admin_required
// from controllers.report_controller import ReportController
// from blueprint.models import User, Profile, Report
// import json

// report_bp = Blueprint('report', __name__, url_prefix='/report')

// @report_bp.route('/submit', methods=['GET', 'POST'])
// @login_required
// def submit_report():
//     if request.method == 'POST':
//         try:
//             reported_user_id = request.form.get('reported_user_id')
//             report_type = request.form.get('report_type')
//             title = request.form.get('title')
//             description = request.form.get('description')
//             severity = request.form.get('severity', 'Medium')
//             evidence_urls = request.form.getlist('evidence_urls')

//             if not all([reported_user_id, report_type, title, description]):
//                 if request.is_json:
//                     return jsonify({'success': False, 'message': 'All fields are required'})
//                 flash('All fields are required', 'error')
//                 return redirect(request.url)

//             result = ReportController.create_report(
//                 reporter_id=session['user_id'],
//                 reported_id=int(reported_user_id),
//                 report_type=report_type,
//                 title=title,
//                 description=description,
//                 evidence_urls=evidence_urls if evidence_urls else None,
//                 severity=severity
//             )

//             if request.is_json:
//                 return jsonify(result)

//             if result['success']:
//                 flash(result['message'], 'success')
//                 return redirect(url_for('report.my_reports'))
//             else:
//                 flash(result['message'], 'error')
//                 return redirect(request.url)
//         except Exception as e:
//             error_msg = f'Error submitting report: {str(e)}'
//             if request.is_json:
//                 return jsonify({'success': False, 'message': error_msg})
//             flash(error_msg, 'error')
//             return redirect(request.url)

//     reported_user_id = request.args.get('user_id')
//     reported_user = None
//     if reported_user_id:
//         reported_user = User.query.get(reported_user_id)

//     report_types = ReportController.get_report_types()
//     severity_levels = ReportController.get_severity_levels()

//     return render_template('reports/quick_report.html',
//                            reported_user=reported_user,
//                            report_types=report_types,
//                            severity_levels=severity_levels)

// @report_bp.route('/my-reports')
// @login_required
// def my_reports():
//     reports_made = ReportController.get_user_reports(session['user_id'], 'made')

//     reports_serialized = []
//     for r in reports_made:
//         reports_serialized.append({
//             'id': r.id,
//             'report_type': r.report_type,
//             'title': r.title,
//             'description': r.description,
//             'severity': r.severity,
//             'status': r.status,
//             'created_at': r.created_at.isoformat(),
//             'admin_notes': r.admin_notes,
//             'resolution': r.resolution,
//             'reported': {
//                 'email': r.reported.email if r.reported else None,
//                 'profile': {
//                     'name': r.reported.profile.name if r.reported and r.reported.profile else None
//                 }
//             }
//         })

//     return render_template('reports/my_reports.html', reports=reports_serialized)

// @report_bp.route('/admin')
// @admin_required
// def admin_dashboard():
//     status_filter = request.args.get('status')
//     severity_filter = request.args.get('severity')
//     search_term = request.args.get('search')
//     search_type = request.args.get('search_type', 'all')

//     if search_term:
//         reports = ReportController.search_reports(search_term, search_type)
//     else:
//         reports = ReportController.get_all_reports(status_filter, severity_filter)

//     statistics = ReportController.get_report_statistics()
//     report_types = ReportController.get_report_types()
//     severity_levels = ReportController.get_severity_levels()

//     return render_template('reports/admin_dashboard.html',
//                            reports=reports,
//                            statistics=statistics,
//                            report_types=report_types,
//                            severity_levels=severity_levels,
//                            current_status=status_filter,
//                            current_severity=severity_filter,
//                            search_term=search_term,
//                            search_type=search_type)

// @report_bp.route('/admin/update-status', methods=['POST'])
// @admin_required
// def update_report_status():
//     try:
//         report_id = request.form.get('report_id')
//         new_status = request.form.get('status')
//         admin_notes = request.form.get('admin_notes')
//         resolution = request.form.get('resolution')

//         if not all([report_id, new_status]):
//             if request.is_json:
//                 return jsonify({'success': False, 'message': 'Report ID and status are required'})
//             flash('Report ID and status are required', 'error')
//             return redirect(request.referrer or url_for('report.admin_dashboard'))

//         result = ReportController.update_report_status(
//             report_id=int(report_id),
//             new_status=new_status,
//             admin_id=session['user_id'],
//             admin_notes=admin_notes,
//             resolution=resolution
//         )

//         if result and result.get('success'):
//             return jsonify({'success': True, 'message': result.get('message', 'Status updated')})
//         else:
//             return jsonify({'success': False, 'message': result.get('message', 'Failed to update status')}), 400

//     except Exception as e:
//         error_msg = f'Error updating report: {str(e)}'
//         if request.is_json:
//             return jsonify({'success': False, 'message': error_msg})
//         flash(error_msg, 'error')
//         return redirect(request.referrer or url_for('report.admin_dashboard'))

// @report_bp.route('/admin/report/<int:report_id>')
// @admin_required
// def view_report_details(report_id):
//     report = Report.query.get_or_404(report_id)

//     evidence_urls = []
//     if report.evidence_urls:
//         try:
//             evidence_urls = json.loads(report.evidence_urls)
//         except:
//             evidence_urls = []

//     return render_template('reports/report_details.html',
//                            report=report,
//                            evidence_urls=evidence_urls)

// @report_bp.route('/admin/statistics')
// @admin_required
// def report_statistics():
//     statistics = ReportController.get_report_statistics()

//     from datetime import datetime, timedelta
//     from sqlalchemy import func
//     from blueprint.models import Report
//     from extensions import db

//     reports_by_type = db.session.query(
//         Report.report_type,
//         func.count(Report.id).label('count')
//     ).group_by(Report.report_type).all()

//     six_months_ago = datetime.now() - timedelta(days=180)
//     reports_by_month = db.session.query(
//         func.date_trunc('month', Report.created_at).label('month'),
//         func.count(Report.id).label('count')
//     ).filter(Report.created_at >=

// //  controllers/admin_controller.py
// from blueprint.models import User, Report
// from extensions import db

// class AdminController:

//     @staticmethod
//     def delete_user(user_id):
//         user = User.query.get(user_id)
//         if user:
//             user.deleted = True
//             db.session.commit()
//             return True, f"User {user.email} has been deleted."
//         return False, "User not found."

//     @staticmethod
//     def toggle_ban_user(user_id):
//         user = User.query.get(user_id)
//         if user:
//             user.active = not user.active
//             db.session.commit()
//             status = "unbanned" if user.active else "banned"
//             return True, f"User {user.email} has been {status}."
//         return False, "User not found."

//     @staticmethod
//     def approve_role_change(user_id):
//         user = User.query.get(user_id)
//         if user and user.pending_role:
//             user.role = user.pending_role
//             user.pending_role = None
//             db.session.commit()
//             return True, f"Role change approved for {user.email}."
//         return False, "User not found or no pending role."

//     @staticmethod
//     def reject_role_change(user_id):
//         user = User.query.get(user_id)
//         if user and user.pending_role:
//             user.pending_role = None
//             db.session.commit()
//             return True, f"Role change rejected for {user.email}."
//         return False, "User not found or no pending role."

//     @staticmethod
//     def get_all_users():
//         return User.query.all()

//     @staticmethod
//     def get_all_reports():
//         return Report.query.all()

//     @staticmethod
//     def get_role_requests():
//         return User.query.filter(User.pending_role.isnot(None)).all()

// This only got dashboard controller
// # controllers/dashboard_controller.py
// # Controller class that handles dashboard-specific data logic for seekers, escorts, and admins.
// # Includes calculations of earnings, spending, and summary analytics.

// from blueprint.models import Booking, User, Favourite, Profile, Payment, Report
// from extensions import db
// from sqlalchemy import func, text

// class DashboardController:

//     @staticmethod
//     def get_user_spending_summary(user_id):
//         if not user_id:
//             return None

//         total_spent = db.session.query(func.sum(Payment.amount)).filter_by(user_id=user_id).scalar() or 0
//         total_transactions = db.session.query(func.count(Payment.id)).filter_by(user_id=user_id).scalar() or 0

//         monthly_breakdown = db.session.query(
//             func.date_trunc('month', Payment.created_at).label('month'),
//             func.sum(Payment.amount).label('total')
//         ).filter(
//             Payment.user_id == user_id
//         ).group_by(
//             func.date_trunc('month', Payment.created_at)
//         ).order_by(text('month desc')).limit(6).all()

//         breakdown = [
//             {"month": month.strftime("%Y-%m"), "total": float(total)}
//             for month, total in monthly_breakdown
//         ]

//         return {
//             "total_spent": round(float(total_spent), 2),
//             "transaction_count": total_transactions,
//             "monthly_breakdown": breakdown
//         }

//     @staticmethod
//     def get_user_earning_summary(user_id):
//         if not user_id:
//             return None

//         total_earned = db.session.query(func.sum(Payment.amount))\
//             .join(Booking, Payment.booking_id == Booking.id)\
//             .filter(Booking.escort_id == user_id).scalar() or 0

//         total_paid_bookings = db.session.query(func.count(Payment.id))\
//             .join(Booking, Payment.booking_id == Booking.id)\
//             .filter(Booking.escort_id == user_id).scalar()

//         monthly_earnings = db.session.query(
//             func.date_trunc('month', Payment.created_at).label('month'),
//             func.sum(Payment.amount).label('total')
//         ).join(Booking, Payment.booking_id == Booking.id)\
//          .filter(Booking.escort_id == user_id)\
//          .group_by(func.date_trunc('month', Payment.created_at))\
//          .order_by(text('month desc')).limit(6).all()

//         breakdown = [
//             {"month": month.strftime("%Y-%m"), "total": float(total)}
//             for month, total in monthly_earnings
//         ]

//         return {
//             "total_earned": round(float(total_earned), 2),
//             "paid_bookings": total_paid_bookings,
//             "monthly_breakdown": breakdown
//         }

//     @staticmethod
//     def get_favourite_profiles(user_id):
//         favourite_ids = [f.favourite_user_id for f in Favourite.query.filter_by(user_id=user_id).all()]
//         if favourite_ids:
//             return Profile.query.filter(Profile.user_id.in_(favourite_ids)).all()
//         return []

//     @staticmethod
//     def get_upcoming_bookings_count(user_id):
//         return db.session.query(Booking).join(
//             User, Booking.escort_id == User.id
//         ).filter(
//             Booking.seeker_id == user_id,
//             Booking.status == 'Confirmed',
//             User.deleted == False,
//             User.active == True,
//             User.activate == True
//         ).count()

//     @staticmethod
//     def get_booking_requests_count(user_id):
//         return db.session.query(Booking).join(
//             User, Booking.seeker_id == User.id
//         ).filter(
//             Booking.escort_id == user_id,
//             Booking.status == 'Pending',
//             User.deleted == False,
//             User.active == True,
//             User.activate == True
//         ).count()

//     @staticmethod
//     def get_admin_dashboard_counts():
//         total_users = User.query.count()
//         total_reports = Report.query.filter_by(status='Pending Review').count()
//         seeker_to_escort = User.query.filter(User.role == 'seeker', User.pending_role == 'escort').count()
//         escort_to_seeker = User.query.filter(User.role == 'escort', User.pending_role == 'seeker').count()

//         return {
//             'total_users': total_users,
//             'total_reports': total_reports,
//             'seeker_to_escort_requests': seeker_to_escort,
//             'escort_to_seeker_requests': escort_to_seeker
//         }

// <<entity>>
// User
// ------------------------------
// + id: Integer
// + email: String
// + password_hash: String
// + role: String
// + active: Boolean
// + created_at: DateTime
// + gender: String
// + pending_role: String
// + activate: Boolean
// + deleted: Boolean
// + email_verified: Boolean
// + email_verification_token: String
// + email_verification_token_expires: DateTime
// + phone_number: String
// + phone_verified: Boolean
// + otp_code: String
// + otp_expires: DateTime
// + otp_attempts: Integer
// + password_created_at: DateTime
// + password_expires_at: DateTime
// + password_change_required: Boolean
// + failed_login_attempts: Integer
// + account_locked_until: DateTime
// ------------------------------
// + set_password(password): (bool, str)
// + add_password_to_history(password_hash): void
// + is_password_in_history(password): bool
// + is_password_expired(): bool
// + days_until_password_expires(): int
// + is_account_locked(): bool
// + increment_failed_login(): str
// + reset_failed_logins(): void
// + is_available(): bool
// + get_display_name(): str
// + check_password(password): bool

// <<entity>>
// Profile
// ------------------------------
// + id: Integer
// + user_id: Integer
// + name: String
// + bio: Text
// + photo: String
// + availability: String
// + rating: Float
// + age: Integer
// + preference: String

// <<entity>>
// Booking
// ------------------------------
// + id: Integer
// + seeker_id: Integer
// + escort_id: Integer
// + start_time: DateTime
// + end_time: DateTime
// + status: String
// ------------------------------
// + __repr__(): String

// <<entity>>
// Payment
// ------------------------------
// + id: Integer
// + user_id: Integer
// + amount: Float
// + status: String
// + transaction_id: String
// + created_at: DateTime
// + booking_id: Integer

// <<entity>>
// Report
// ------------------------------
// + id: Integer
// + reporter_id: Integer
// + reported_id: Integer
// + report_type: String
// + title: String
// + description: Text
// + evidence_urls: Text
// + severity: String
// + status: String
// + admin_notes: Text
// + resolution: Text
// + created_at: DateTime
// + updated_at: DateTime
// + resolved_at: DateTime
// + assigned_admin_id: Integer
// ------------------------------
// + __repr__(): String

// <<entity>>
// TimeSlot
// ------------------------------
// + id: Integer
// + user_id: Integer
// + start_time: DateTime
// + end_time: DateTime

// <<entity>>
// Message
// ------------------------------
// + id: Integer
// + sender_id: Integer
// + recipient_id: Integer
// + content: Text
// + timestamp: DateTime
// + is_read: Boolean
// + deleted_by_sender: Boolean
// + deleted_by_recipient: Boolean
// ------------------------------
// + __repr__(): String

// <<entity>>
// Rating
// ------------------------------
// + id: Integer
// + booking_id: Integer
// + reviewer_id: Integer
// + reviewed_id: Integer
// + rating: Integer
// + feedback: Text
// + created_at: DateTime
// ------------------------------
// + __repr__(): String

// <<entity>>
// PasswordHistory
// ------------------------------
// + id: Integer
// + user_id: Integer
// + password_hash: String
// + created_at: DateTime
// ------------------------------
// + __repr__(): String

// <<entity>>
// Favourite
// ------------------------------
// + id: Integer
// + user_id: Integer
// + favourite_user_id: Integer
// + created_at: DateTime
// ------------------------------
// + __repr__(): String

// <<entity>>
// AuditLog
// ------------------------------
// + id: Integer
// + user_id: Integer
// + action: String
// + details: Text
// + created_at: DateTime
// ------------------------------
// + __repr__(): String

// controllers/rating_controller.py
// from blueprint.models import Rating, Booking
// from extensions import db

// class RatingController:

//     @staticmethod
//     def submit_rating(booking_id, reviewer_id, rating_value, feedback=''):
//         # Check if rating exists for booking + reviewer
//         existing = Rating.query.filter_by(booking_id=booking_id, reviewer_id=reviewer_id).first()
//         if existing:
//             return False, "You have already rated this booking."

//         # Create rating
//         new_rating = Rating(
//             booking_id=booking_id,
//             reviewer_id=reviewer_id,
//             rating=rating_value,
//             feedback=feedback
//         )
//         db.session.add(new_rating)
//         db.session.commit()
//         return True, new_rating

//     @staticmethod
//     def get_user_ratings(user_id, limit=None):
//         query = Rating.query.filter_by(reviewee_id=user_id).order_by(Rating.created_at.desc())
//         if limit:
//             query = query.limit(limit)
//         return query.all()

//     @staticmethod
//     def get_user_given_ratings(user_id):
//         return Rating.query.filter_by(reviewer_id=user_id).order_by(Rating.created_at.desc()).all()

//     @staticmethod
//     def get_rating_statistics(user_id):
//         from sqlalchemy import func
//         avg_rating = db.session.query(func.avg(Rating.rating)).filter_by(reviewee_id=user_id).scalar() or 0
//         count = db.session.query(func.count(Rating.id)).filter_by(reviewee_id=user_id).scalar() or 0
//         return {"average_rating": round(avg_rating, 2), "count": count}

//     @staticmethod
//     def get_rateable_bookings(user_id):
//         # Bookings user can rate (e.g. completed bookings without rating)
//         # Simplified example: bookings with status 'Completed' and not yet rated by user
//         rated_booking_ids = [r.booking_id for r in Rating.query.filter_by(reviewer_id=user_id).all()]
//         bookings = Booking.query.filter(
//             ((Booking.seeker_id == user_id) | (Booking.escort_id == user_id)),
//             Booking.status == 'Completed',
//             ~Booking.id.in_(rated_booking_ids)
//         ).all()
//         return bookings

//     @staticmethod
//     def get_booking_ratings(booking_id):
//         return Rating.query.filter_by(booking_id=booking_id).all()

// controllers/report_controller.py
// from blueprint.models import Report
// from extensions import db
// import json

// class ReportController:

//     @staticmethod
//     def create_report(reporter_id, reported_id, report_type, title, description, evidence_urls=None, severity='Medium'):
//         try:
//             evidence_json = json.dumps(evidence_urls) if evidence_urls else None
//             report = Report(
//                 reporter_id=reporter_id,
//                 reported_id=reported_id,
//                 report_type=report_type,
//                 title=title,
//                 description=description,
//                 evidence_urls=evidence_json,
//                 severity=severity,
//                 status='Pending Review'
//             )
//             db.session.add(report)
//             db.session.commit()
//             return {'success': True, 'message': 'Report submitted successfully.'}
//         except Exception as e:
//             db.session.rollback()
//             return {'success': False, 'message': f'Failed to submit report: {str(e)}'}

//     @staticmethod
//     def get_report_types():
//         # Example static list; replace with DB if dynamic
//         return ['Spam', 'Harassment', 'Inappropriate Content', 'Other']

//     @staticmethod
//     def get_severity_levels():
//         return ['Low', 'Medium', 'High', 'Critical']

//     @staticmethod
//     def get_user_reports(user_id, mode='made'):
//         if mode == 'made':
//             return Report.query.filter_by(reporter_id=user_id).order_by(Report.created_at.desc()).all()
//         elif mode == 'received':
//             return Report.query.filter_by(reported_id=user_id).order_by(Report.created_at.desc()).all()
//         return []

//     @staticmethod
//     def get_all_reports(status_filter=None, severity_filter=None):
//         query = Report.query
//         if status_filter:
//             query = query.filter_by(status=status_filter)
//         if severity_filter:
//             query = query.filter_by(severity=severity_filter)
//         return query.order_by(Report.created_at.desc()).all()

//     @staticmethod
//     def update_report_status(report_id, new_status, admin_id, admin_notes=None, resolution=None):
//         report = Report.query.get(report_id)
//         if not report:
//             return {'success': False, 'message': 'Report not found'}
//         report.status = new_status
//         report.admin_notes = admin_notes
//         report.resolution = resolution
//         report.admin_id = admin_id
//         try:
//             db.session.commit()
//             return {'success': True, 'message': 'Report status updated'}
//         except Exception as e:
//             db.session.rollback()
//             return {'success': False, 'message': f'Error updating report: {str(e)}'}

//     @staticmethod
//     def get_report_statistics():
//         # You can customize the statistics returned here
//         from sqlalchemy import func
//         total_reports = Report.query.count()
//         pending_reports = Report.query.filter_by(status='Pending Review').count()
//         resolved_reports = Report.query.filter(Report.status.in_(['Resolved', 'Closed'])).count()
//         return {
//             'total_reports': total_reports,
//             'pending_reports': pending_reports,
//             'resolved_reports': resolved_reports
//         }

//     @staticmethod
//     def search_reports(search_term, search_type='all'):
//         # Simplified example: search by title or description
//         from sqlalchemy import or_
//         query = Report.query
//         if search_type == 'title':
//             query = query.filter(Report.title.ilike(f'%{search_term}%'))
//         elif search_type == 'description':
//             query = query.filter(Report.description.ilike(f'%{search_term}%'))
//         else:
//             query = query.filter(or_(
//                 Report.title.ilike(f'%{search_term}%'),
//                 Report.description.ilike(f'%{search_term}%')
//             ))
//         return query.order_by(Report.created_at.desc()).all()

// #controllers/profile_controller.py
// from blueprint.models import Profile, User
// from extensions import db

// class ProfileController:

//     @staticmethod
//     def get_profile_by_user_id(user_id):
//         return Profile.query.filter_by(user_id=user_id).first()

//     @staticmethod
//     def update_profile(user_id, name=None, bio=None, availability=None, photo_url=None):
//         profile = Profile.query.filter_by(user_id=user_id).first()
//         if not profile:
//             return False, "Profile not found"
//         if name is not None:
//             profile.name = name
//         if bio is not None:
//             profile.bio = bio
//         if availability is not None:
//             profile.availability = availability
//         if photo_url:
//             profile.photo = photo_url
//         db.session.commit()
//         return True, "Profile updated"

//     @staticmethod
//     def request_role_change(user):
//         if user.role == 'seeker':
//             user.pending_role = 'escort'
//         elif user.role == 'escort':
//             user.pending_role = 'seeker'
//         else:
//             return False, "Role change not allowed"
//         db.session.commit()
//         return True, "Role change requested"

//     @staticmethod
//     def deactivate_user(user):
//         user.activate = False
//         db.session.commit()
//         return True

// Boundary classes:
// profile.py

// from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
// from blueprint.decorators import login_required
// from blueprint.audit_log import log_event
// from extensions import csrf
// from controllers.profile_controller import ProfileController
// from blueprint.models import User

// profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

// @profile_bp.route('/', methods=['GET', 'POST'])
// @login_required
// def profile():
//     user_id = session['user_id']
//     if request.method == 'POST':
//         success, msg = ProfileController.update_profile(
//             user_id,
//             name=request.form.get('name'),
//             bio=request.form.get('bio'),
//             availability=request.form.get('availability'),
//             photo_url=request.form.get('photo_url')
//         )
//         if success:
//             flash(msg, 'success')
//             return redirect(url_for('profile.profile'))
//         else:
//             flash(msg, 'danger')
//             return redirect(url_for('profile.profile'))

//     user_profile = ProfileController.get_profile_by_user_id(user_id)
//     return render_template('profile.html', profile=user_profile)

// @profile_bp.route('/photo', methods=['GET'])
// @login_required
// def get_profile_photo():
//     user_id = session.get('user_id')
//     profile = ProfileController.get_profile_by_user_id(user_id)
//     if not profile:
//         return jsonify({'error': 'Profile not found'}), 404
//     return jsonify({
//         'user_id': user_id,
//         'photo_url': profile.photo or ' https://via.placeholder.com/150'
//     })

// @profile_bp.route('/request-role-change', methods=['POST'])
// @login_required
// def request_role_change():
//     user = User.query.get(session['user_id'])
//     success, msg = ProfileController.request_role_change(user)
//     flash(msg, 'info' if success else 'warning')
//     if success:
//         log_event(user.id, 'role change request', f"User {user.email} requested role change.")
//     else:
//         log_event(user.id, 'role change failed', f"User {user.email} attempted invalid role change.")
//     return redirect(url_for('profile.profile'))

// @profile_bp.route('/deactivate', methods=['POST'])
// @login_required
// def deactivate_profile():
//     user = User.query.get(session['user_id'])
//     success = ProfileController.deactivate_user(user)
//     if success:
//         session.clear()
//         flash("Your account has been deactivated. You are now logged out.", "info")
//         log_event(user.id, 'deactivate', f"User {user.email} deactivated their account.")
//     else:
//         flash("Failed to deactivate account.", "danger")
//     return redirect(url_for('auth.auth', mode='login'))

// // controllers/auth_controller.py

// from blueprint.models import User
// from extensions import db
// from werkzeug.security import generate_password_hash, check_password_hash

// class AuthController:
//     @staticmethod
//     def register(email, password):
//         if User.query.filter_by(email=email).first():
//             return False  # Email already exists

//         hashed_password = generate_password_hash(password)
//         new_user = User(email=email, password=hashed_password, role='seeker', active=True, activate=True)
//         db.session.add(new_user)
//         db.session.commit()
//         return True

//     @staticmethod
//     def authenticate(email, password):
//         user = User.query.filter_by(email=email, active=True, activate=True).first()
//         if user and check_password_hash(user.password, password):
//             return True
//         return False

// /* or */
// // >? controllers/auth_controller.py
// from blueprint.models import User
// from extensions import db
// from werkzeug.security import generate_password_hash, check_password_hash

// class AuthController:

//     @staticmethod
//     def authenticate(email: str, password: str) -> bool:
//         user = User.query.filter_by(email=email, deleted=False).first()
//         if not user or not user.active or not user.activate:
//             return False
//         if check_password_hash(user.password_hash, password):
//             return True
//         return False

//     @staticmethod
//     def register(email: str, password: str) -> bool:
//         if User.query.filter_by(email=email).first():
//             return False
//         hashed_pw = generate_password_hash(password)
//         new_user = User(email=email, password_hash=hashed_pw, role='seeker', active=True, activate=True)
//         db.session.add(new_user)
//         db.session.commit()
//         return True

//  Boundary:
// rating.py

// from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
// from blueprint.decorators import login_required
// from controllers.rating_controller import RatingController
// from blueprint.models import User, Profile, Booking

// rating_bp = Blueprint('rating', __name__, url_prefix='/rating')

// @rating_bp.route('/submit', methods=['POST'])
// @login_required
// def submit_rating():
//     data = request.get_json()
//     booking_id = data.get('booking_id')
//     rating_value = data.get('rating')
//     feedback = data.get('feedback', '')
//     if not booking_id or not rating_value:
//         return jsonify({'success': False, 'error': 'Missing required fields'})
//     try:
//         rating_value = int(rating_value)
//     except (ValueError, TypeError):
//         return jsonify({'success': False, 'error': 'Invalid rating value'})

//     success, result = RatingController.submit_rating(
//         booking_id=booking_id,
//         reviewer_id=session['user_id'],
//         rating_value=rating_value,
//         feedback=feedback
//     )
//     if success:
//         return jsonify({'success': True,
