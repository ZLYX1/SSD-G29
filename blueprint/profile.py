
import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from blueprint.models import Profile
from extensions import db
from blueprint.decorators import login_required


profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

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
        user_profile.name = request.form.get('name')
        user_profile.bio = request.form.get('bio')
        user_profile.availability = request.form.get('availability')
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))
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
            Fiields={"Content-Type": file_type},
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