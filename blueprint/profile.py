import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from blueprint.models import Profile
from extensions import db
from blueprint.decorators import login_required
import re

# Try to import boto3 for S3 functionality (optional dependency)
try:
    import boto3
    from botocore.exceptions import ClientError
    s3 = boto3.client('s3')
    HAS_S3 = True
except ImportError:
    HAS_S3 = False
    s3 = None


profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

def validate_profile_data(name, bio, availability):
    """Validate profile form data"""
    errors = []
    
    # Name validation
    if not name or not name.strip():
        errors.append("Name is required")
    elif len(name.strip()) < 2:
        errors.append("Name must be at least 2 characters long")
    elif len(name.strip()) > 100:
        errors.append("Name must be less than 100 characters")
    elif not re.match(r'^[a-zA-Z\s\-\.]+$', name.strip()):
        errors.append("Name can only contain letters, spaces, hyphens, and periods")
    
    # Bio validation
    if bio and len(bio.strip()) > 500:
        errors.append("Bio must be less than 500 characters")
    
    # Availability validation
    valid_availability = ["Available", "Temporarily Unavailable"]
    if availability not in valid_availability:
        errors.append("Invalid availability status")
    
    return errors

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

# @app.route('/profile', methods=['GET', 'POST'])
@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def profile():
    user_profile = Profile.query.filter_by(user_id=session['user_id']).first()
    if request.method == 'POST':
        name = request.form.get('name')
        bio = request.form.get('bio')
        availability = request.form.get('availability')

        # Validate profile data
        errors = validate_profile_data(name, bio, availability)
        if errors:
            for error in errors:
                flash(error, "danger")
            return redirect(url_for('profile.profile'))

        user_profile.name = name
        user_profile.bio = bio
        user_profile.availability = availability
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile.profile'))
    return render_template('profile.html', profile=user_profile)

# For pre-signed url
@profile_bp.route('/generate-presigned-url', methods=['POST'])
@login_required
def generate_presigned_url():
    file_name = request.json.get('file_name')
    file_type = request.json.get('file_type')
    S3_BUCKET = os.environ['S3_BUCKET_NAME']
    
    if not file_name or not file_type:
        return {'error': 'Missing file name or type'}, 400

  	# ✅ file type validation here
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file_type not in allowed_types:
        return {'error': 'Invalid file type'}, 400

    try:
        presigned_post = s3.generate_presigned_post(
            Bucket=S3_BUCKET,
            Key=f"profile_photos/{session['user_id']}/{file_name}",
            Fields={"Content-Type": file_type},
            Conditions=[
                {"Content-Type": file_type}
            ],
            ExpiresIn=300
        )
        return presigned_post
    except Exception as e:
        return {'error': str(e)}, 500
    
@profile_bp.route('/save-photo', methods=['POST'])
@login_required
def save_photo():
    photo_url = request.json.get('photo_url')
    if not photo_url:
        return {'error': 'Missing photo URL'}, 400

    user_profile = Profile.query.filter_by(user_id=session['user_id']).first()
    user_profile.photo = photo_url  # or just the filename if preferred
    db.session.commit()

    return {'message': 'Photo saved successfully'}, 200

@profile_bp.route('/photo', methods=['GET'])
@login_required
def get_profile_photo():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({'error': 'Profile not found'}), 404

    return jsonify({
        'user_id': user_id,
        'photo_url': profile.photo or 'https://via.placeholder.com/150'
    }), 200