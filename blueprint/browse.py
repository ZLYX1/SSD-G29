from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from blueprint.models import Profile, User, TimeSlot, Booking, Favourite
from extensions import db
from blueprint.decorators import login_required
from datetime import datetime, time
from flask_wtf.csrf import generate_csrf
from sqlalchemy import and_
from flask import jsonify
from datetime import timedelta

browse_bp = Blueprint('browse', __name__, url_prefix='/browse')

# @browse_bp.route('/browse', methods=['GET', 'POST'])
# @login_required
# def browseEscort():
#     escort_profiles = (Profile.query.join(User)
#     # .filter(User.role == 'escort')
#     .filter(User.role == 'escort', User.activate == True)
#     .all())
#     return render_template('browse.html', profiles=escort_profiles)

# Should have 1 for escorts to see
@browse_bp.route('/browseSeeker', methods=['GET', 'POST'])
@login_required
def browseSeeker():
    user_role = 'escort'
     
    # escort_profiles = (Profile.query.join(User)
    # # .filter(User.role == 'escort')
    # .filter(User.role == 'seeker', User.active == True)
    # .all())
    # return render_template('browse.html', profiles=escort_profiles)
    query = Profile.query.join(User).filter(
        User.role == 'seeker',
        User.active == True,
        User.deleted == False
    )

    # Extract query parameters
    min_age = request.args.get('min_age', type=int)
    max_age = request.args.get('max_age', type=int)
    gender = request.args.get('gender')
    min_rating = request.args.get('min_rating', type=float)
    avail_date = request.args.get('avail_date')
    avail_time = request.args.get('avail_time')

    # Apply basic filters
    if min_age is not None:
        query = query.filter(Profile.age >= min_age)
    if max_age  is not None:
        query = query.filter(Profile.age <= max_age)
    if gender:
        query = query.filter(User.gender == gender)
    if min_rating is not None:
        query = query.filter(Profile.rating >= min_rating)

    query = Profile.query.join(User).filter(User.role == 'seeker').limit(5)
    profiles = query.all()
    print(profiles)  # see if this returns anything
    favourite_ids = [f.favourite_user_id for f in Favourite.query.filter_by(user_id=session['user_id']).all()]
    return render_template('browse.html', profiles=profiles, user_role=user_role, favourited_ids=favourite_ids)

def get_valid_start_times(slot, duration_minutes, escort_id):
    valid_starts = []
    current_start = slot.start_time
    end_limit = slot.end_time - timedelta(minutes=duration_minutes)
    
    while current_start <= end_limit:
        current_end = current_start + timedelta(minutes=duration_minutes)
        # Check for conflicting bookings for escort during this interval
        conflict = Booking.query.filter(
            Booking.escort_id == escort_id,
            Booking.status.in_(["Pending", "Confirmed"]),
            Booking.start_time < current_end,
            Booking.end_time > current_start
        ).first()
        if not conflict and current_start >= datetime.utcnow():
            valid_starts.append(current_start)
        current_start += timedelta(minutes=15)  # increment by 15 mins
    return valid_starts


@browse_bp.route('/profile/<int:user_id>')
@login_required
def view_profile(user_id):
    profile = Profile.query.join(User).filter(
        Profile.user_id == user_id,
        User.deleted == False,  # Exclude deleted users
        User.active == True     # Only show active users
    ).first()
    
    if not profile:
        flash("Escort not found.", "danger")
        return redirect(url_for('home'))

    available_slots = TimeSlot.query.filter(
        TimeSlot.user_id == user_id,
        TimeSlot.start_time >= datetime.utcnow()
    ).order_by(TimeSlot.start_time.asc()).all()


    # For each slot, generate valid start times for default duration (e.g., 15 mins)
    slots_with_start_times = []
    default_duration = 15
    for slot in available_slots:
        valid_starts = get_valid_start_times(slot, default_duration, user_id)
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

# 2. PROFILE MANAGEMENT
# @app.route('/profile', methods=['GET', 'POST'])
# @login_required
# def profile():
#     user_id = session['user_id']
#     user_profile = PROFILES.get(user_id)

#     if request.method == 'POST':
#         # Simulate updating profile
#         user_profile['name'] = request.form.get('name')
#         user_profile['bio'] = request.form.get('bio')
#         # Simulate photo upload
#         if 'photo' in request.files and request.files['photo'].filename != '':
#             user_profile['photo'] = 'new_photo.jpg' # Dummy filename
#         flash("Profile updated successfully!", "success")
#         return redirect(url_for('profile'))

#     return render_template('profile.html', profile=user_profile)

# # @app.route('/profile', methods=['GET', 'POST'])
# @profile_bp.route('/', methods=['GET', 'POST'])
# @login_required
# def profile():
#     user_profile = Profile.query.filter_by(user_id=session['user_id']).first()
#     if request.method == 'POST':
#         user_profile.name = request.form.get('name')
#         user_profile.bio = request.form.get('bio')
#         user_profile.availability = request.form.get('availability')
#         db.session.commit()
#         flash("Profile updated successfully!", "success")
#         return redirect(url_for('profile'))
#     return render_template('profile.html', profile=user_profile)

# # For pre-signed url
# @profile_bp.route('/generate-presigned-url', methods=['POST'])
# @login_required
# def generate_presigned_url():
#     file_name = request.json.get('file_name')
#     file_type = request.json.get('file_type')
#     S3_BUCKET = os.environ['S3_BUCKET_NAME']

#     if not file_name or not file_type:
#         return {'error': 'Missing file name or type'}, 400

#   	# ✅ file type validation here
#     allowed_types = ["image/jpeg", "image/png", "image/jpg"]
#     if file_type not in allowed_types:
#         return {'error': 'Invalid file type'}, 400

#     try:
#         presigned_post = s3.generate_presigned_post(
#             Bucket=S3_BUCKET,
#             Key=f"profile_photos/{session['user_id']}/{file_name}",
#             Fiields={"Content-Type": file_type},
#             Conditions=[
#                 {"Content-Type": file_type}
#             ],
#             ExpiresIn=300
#         )
#         return presigned_post
#     except Exception as e:
#         return {'error': str(e)}, 500

# @profile_bp.route('/save-photo', methods=['POST'])
# @login_required
# def save_photo():
#     photo_url = request.json.get('photo_url')
#     if not photo_url:
#         return {'error': 'Missing photo URL'}, 400

#     user_profile = Profile.query.filter_by(user_id=session['user_id']).first()
#     user_profile.photo = photo_url  # or just the filename if preferred
#     db.session.commit()

#     return {'message': 'Photo saved successfully'}, 200


def can_book(escort_id, new_start, new_end):
    # 1. Check if escort has availability covering the requested time
    available_slot = TimeSlot.query.filter(
        TimeSlot.user_id == escort_id,
        TimeSlot.start_time <= new_start,
        TimeSlot.end_time >= new_end
    ).first()

    if not available_slot:
        return False, "Escort is not available for the requested time."

    # 2. Check for overlapping bookings (Pending or Confirmed)
    overlapping_booking = Booking.query.filter(
        Booking.escort_id == escort_id,
        Booking.status.in_(["Pending", "Confirmed"]),
        Booking.start_time < new_end,
        Booking.end_time > new_start
    ).first()

    if overlapping_booking:
        return False, "The escort already has a booking that conflicts with this time."

    # If all good
    return True, "Time slot is available for booking."


@browse_bp.route('/browse', methods=['GET'])
@login_required
def browseEscort():
    user_role = 'seeker'
    query = Profile.query.join(User).filter(
        User.role == 'escort', 
		User.active == True,
  		User.deleted == False
    )

    # Extract query parameters
    min_age = request.args.get('min_age', type=int)
    max_age = request.args.get('max_age', type=int)
    gender = request.args.get('gender')
    min_rating = request.args.get('min_rating', type=float)
    
    avail_date = request.args.get('avail_date')
    avail_time = request.args.get('avail_time')
    
    # print("log avail_date")
    # print(avail_date)
    # print("avail_time")
    # print(avail_time)

    # Apply basic filters
    if min_age:
        query = query.filter(Profile.age >= min_age)
    if max_age:
        query = query.filter(Profile.age <= max_age)
    if gender:
        query = query.filter(User.gender == gender)
    if min_rating is not None:
        query = query.filter(Profile.rating >= min_rating)
    
    if avail_date:
        try:
            if avail_time:
                selected_datetime = datetime.strptime(f"{avail_date} {avail_time}", "%Y-%m-%d %H:%M")
                print(selected_datetime)
            else:
                selected_datetime = datetime.combine(datetime.strptime(avail_date, "%Y-%m-%d"), time(0, 0))
                print(selected_datetime)

			# Filter escorts who have a TimeSlot that includes the selected time
            query = query.join(TimeSlot).filter(
				and_(
					TimeSlot.start_time <= selected_datetime,
					TimeSlot.end_time > selected_datetime
				)
			)

			# Subquery to get escorts who are already booked during that time
            overlapping_escorts_subq = db.session.query(Booking.escort_id).filter(
				Booking.status.in_(["Pending", "Confirmed"]),
				Booking.start_time < selected_datetime,
				Booking.end_time > selected_datetime
			).subquery()

			# Exclude those who have a booking at that time
            query = query.filter(~User.id.in_(overlapping_escorts_subq))

        except ValueError:
            pass  # ignore invalid input

    profiles = query.distinct().all()
    favourite_ids = [f.favourite_user_id for f in Favourite.query.filter_by(user_id=session['user_id']).all()]
    
    return render_template('browse.html', profiles=profiles,user_role=user_role, favourited_ids=favourite_ids)


    # query = Profile.query.join(User).filter(User.role == 'escort', User.active == True)

    # min_age = request.args.get('min_age', type=int)
    # max_age = request.args.get('max_age', type=int)
    # availability = request.args.get('availability')
    # min_rating = request.args.get('min_rating', type=float)

    # if min_age is not None:
    #     query = query.filter(Profile.age >= min_age)
    # if max_age is not None:
    #     query = query.filter(Profile.age <= max_age)
    # if availability == 'yes':
    #     query = query.filter(Profile.availability == True)
    # elif availability == 'no':
    #     query = query.filter(Profile.availability == False)
    # if min_rating is not None:
    #     query = query.filter(Profile.rating >= min_rating)

    # escort_profiles = query.all()
    # return render_template('browse.html', profiles=escort_profiles)
