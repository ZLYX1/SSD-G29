from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from blueprint.models import Profile, User, TimeSlot
from extensions import db
from blueprint.decorators import login_required
from datetime import datetime
from flask_wtf.csrf import generate_csrf

browse_bp = Blueprint('browse', __name__, url_prefix='/browse')


# Shoud have 1 for escorts to see
@browse_bp.route('/browseSeeker', methods=['GET', 'POST'])
@login_required
def browseSeeker():
    escort_profiles = (Profile.query.join(User)
                       # .filter(User.role == 'escort')
                       .filter(User.role == 'seeker', User.activate == True)
                       .all())
    return render_template('browse.html', profiles=escort_profiles)


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

    # ✅ ADD csrf_token TO TEMPLATE CONTEXT
    return render_template(
        'view_profile.html',
        profile=profile,
        time_slots=available_slots,
        csrf_token=generate_csrf()
    )


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

# to test
@browse_bp.route('/browse', methods=['GET'])
@login_required
def browseEscort():
    query = Profile.query.join(User).filter(User.role == 'escort', User.activate == True)

    min_age = request.args.get('min_age', type=int)
    max_age = request.args.get('max_age', type=int)
    availability = request.args.get('availability')
    min_rating = request.args.get('min_rating', type=float)

    if min_age is not None:
        query = query.filter(Profile.age >= min_age)
    if max_age is not None:
        query = query.filter(Profile.age <= max_age)
    if availability == 'yes':
        query = query.filter(Profile.availability == True)
    elif availability == 'no':
        query = query.filter(Profile.availability == False)
    if min_rating is not None:
        query = query.filter(Profile.rating >= min_rating)

    escort_profiles = query.all()
    return render_template('browse.html', profiles=escort_profiles)
