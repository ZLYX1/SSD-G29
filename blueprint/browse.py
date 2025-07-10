from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from blueprint.models import Profile, User, TimeSlot, Booking, Favourite
from extensions import db
from blueprint.decorators import login_required
from datetime import datetime, time
from flask_wtf.csrf import generate_csrf
from sqlalchemy import and_
from flask import jsonify
from datetime import timedelta
from blueprint.controller.browse_controller import BrowseController


browse_bp = Blueprint('browse', __name__, url_prefix='/browse')

# Should have 1 for escorts to see
@browse_bp.route('/browseSeeker', methods=['GET', 'POST'])
@login_required
def browseSeeker():
	user_id = session['user_id']
	if not user_id:
		return jsonify({'error': 'Not logged in'}), 401
	user_role = 'escort'

	# query = BrowseController.get_profile('seeker', True, False)

	filters = {
		'min_age': request.args.get('min_age', type=int),
		'max_age': request.args.get('max_age', type=int),
		'gender': request.args.get('gender'),
		'min_rating': request.args.get('min_rating', type=float),
		'avail_date': request.args.get('avail_date'),
		'avail_time': request.args.get('avail_time'),
	}
   
	profiles = BrowseController.get_profiles('seeker', filters, 5)
	# profiles = query.all()
	favourite_ids = BrowseController.get_favourite_ids(user_id)
	return render_template('browse.html', profiles=profiles, user_role=user_role, favourited_ids=favourite_ids)

# def get_valid_start_times(slot, duration_minutes, escort_id):
#     valid_starts = []
#     current_start = slot.start_time
#     end_limit = slot.end_time - timedelta(minutes=duration_minutes)
	
#     while current_start <= end_limit:
#         current_end = current_start + timedelta(minutes=duration_minutes)
#         # Check for conflicting bookings for escort during this interval
#         conflict = BrowseController.get_overlapping(
# 			escort_id=escort_id,
#    			start_time= current_end,
#    			end_time= current_start
# 		)
#         # Booking.query.filter(
#         #     Booking.escort_id == escort_id,
#         #     Booking.status.in_(["Pending", "Confirmed"]),
#         #     Booking.start_time < current_end,
#         #     Booking.end_time > current_start
#         # ).first()
#         if not conflict and current_start >= datetime.utcnow():
#             valid_starts.append(current_start)
#         current_start += timedelta(minutes=15)  # increment by 15 mins
#     return valid_starts


# havent seen
@browse_bp.route('/profile/<int:user_id>')
@login_required
def view_profile(user_id):

	profile = BrowseController.get_specific_profile(user_id, False, True)
	
	if not profile:
		flash("Escort not found.", "danger")
		return redirect(url_for('home'))


	# available_slots = TimeSlot.query.filter(
	#     TimeSlot.user_id == user_id,
	#     TimeSlot.start_time >= datetime.utcnow()
	# ).order_by(TimeSlot.start_time.asc()).all()
	available_slots = BrowseController.get_available_slots(
		user_id=user_id,
  		start_time= datetime.utcnow()
	)

	# For each slot, generate valid start times for default duration (e.g., 15 mins)
	slots_with_start_times = []
	default_duration = 15
	for slot in available_slots:
		valid_starts = BrowseController.get_valid_start_times(slot, default_duration, user_id)
		slots_with_start_times.append({
			'slot': slot,
			'valid_starts': valid_starts
		})
		
	# ✅ ADD csrf_token TO TEMPLATE CONTEXT
	return render_template(
		'view_profile.html',
		profile=profile,
		time_slots=available_slots,
		slots_with_start_times=slots_with_start_times,
		csrf_token=generate_csrf()
	)

# favourite the user. Its working
@browse_bp.route('/favourite/<int:user_id>', methods=['POST'])
@login_required
def toggle_favourite(user_id):
	current_user_id = session['user_id']

	# Check if already favourited
	existing = Favourite.query.filter_by(user_id=current_user_id, favourite_user_id=user_id).first()

	if existing:
		db.session.delete(existing)
		db.session.commit()
		return jsonify({'status': 'removed'})
	else:
		new_fav = Favourite(user_id=current_user_id, favourite_user_id=user_id)
		db.session.add(new_fav)
		db.session.commit()
		return jsonify({'status': 'added'})



@browse_bp.route('/browse', methods=['GET'])
@login_required
def browseEscort():
	user_role = 'seeker'
# query = BrowseController.get_profile('escort', False, True)
	# query = Profile.query.join(User).filter(
	#     User.role == 'escort', 
  	# 	User.deleted == False
	# 	User.active == True,
	# )

	# Extract query parameters
	# min_age = request.args.get('min_age', type=int)
	# max_age = request.args.get('max_age', type=int)
	# gender = request.args.get('gender')
	# min_rating = request.args.get('min_rating', type=float)
	# avail_date = request.args.get('avail_date')
	# avail_time = request.args.get('avail_time')   
	
	# Apply basic filters
	# if min_age:
	#     query = query.filter(Profile.age >= min_age)
	# if max_age:
	#     query = query.filter(Profile.age <= max_age)
	# if gender:
	#     query = query.filter(User.gender == gender)
	# if min_rating is not None:
	#     query = query.filter(Profile.rating >= min_rating)
	
	filters = {
		'min_age': request.args.get('min_age', type=int),
		'max_age': request.args.get('max_age', type=int),
		'gender': request.args.get('gender'),
		'min_rating': request.args.get('min_rating', type=float),
		'avail_date': request.args.get('avail_date'),
		'avail_time': request.args.get('avail_time'),
	}
	 
	# if avail_date:
	#     try:
	#         if avail_time:
	#             selected_datetime = datetime.strptime(f"{avail_date} {avail_time}", "%Y-%m-%d %H:%M")
				
	#         else:
	#             selected_datetime = datetime.combine(datetime.strptime(avail_date, "%Y-%m-%d"), time(0, 0))
				

	# 		# Filter escorts who have a TimeSlot that includes the selected time
	#         query = query.join(TimeSlot).filter(
	# 			and_(
	# 				TimeSlot.start_time <= selected_datetime,
	# 				TimeSlot.end_time > selected_datetime
	# 			)
	# 		)

			# Subquery to get escorts who are already booked during that time
			# overlapping_escorts_subq = db.session.query(Booking.escort_id).filter(
			# 	Booking.status.in_(["Pending", "Confirmed"]),
			# 	Booking.start_time < selected_datetime,
			# 	Booking.end_time > selected_datetime
			# ).subquery()

	profiles = BrowseController.get_profiles(user_role="escort", filters=filters, limit=15)
			
	favourite_ids = [f.favourite_user_id for f in Favourite.query.filter_by(user_id=session['user_id']).all()]
	if not profiles:
		flash("No escorts match your search criteria.", "warning")
	return render_template('browse.html', profiles=profiles,user_role=user_role, favourited_ids=favourite_ids)



