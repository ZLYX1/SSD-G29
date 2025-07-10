import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from blueprint.models import Profile
from extensions import db
from blueprint.decorators import login_required
from blueprint.audit_log import log_event
# from flask_wtf import CSRFProtect
from extensions import db, csrf, s3
from datetime import datetime
from flask import jsonify
from blueprint.models import User  # make sure you have this
from blueprint.controller.profile_controller import ProfileController
import uuid

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def profile():
	user_id = session['user_id']
	if not user_id:
		return jsonify({'error': 'Not logged in'}), 401

	user_profile = ProfileController.get_profile_by_user_id(user_id)

	if request.method == 'POST':
		name = request.form.get('name')
		bio = request.form.get('bio')
		availability = request.form.get('availability')
		photo_url = request.form.get('photo_url')
  
		_, err = ProfileController.update_profile(user_id, name, bio, availability, photo_url)
		if err:
			flash(err, 'danger')
		else:
			flash("Profile updated successfully!", "success")
		return redirect(url_for('profile.profile'))

	return render_template('profile.html', profile=user_profile)

@profile_bp.route('/photo', methods=['GET'])
@login_required
def get_profile_photo():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    profile = ProfileController.get_profile_by_user_id(user_id)

    if not profile:
        return jsonify({'error': 'Profile not found'}), 404

    return jsonify({
        'user_id': user_id,
        'photo_url': profile.photo or 'https://via.placeholder.com/150'
    }), 200
    
    

@profile_bp.route('/generate-presigned-url', methods=['POST'])
@login_required
def generate_presigned_url():
    try:
        file_name = request.json.get('file_name')
        file_type = request.json.get('file_type')
        
        if not file_name or not file_type:
            return jsonify({'error': 'Missing file name or type'}), 400
        
        # ✅ Enforce allowed types
        ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
        if file_type not in ALLOWED_MIME_TYPES:
            return jsonify({'error': 'Invalid file type'}), 400

        # Generate a unique filename to avoid collisions
        ext = file_name.split('.')[-1]
        unique_key = f"profile_photos/{session['user_id']}/{uuid.uuid4()}.{ext}"
        file_url = f"https://{os.environ['S3_BUCKET_NAME']}.s3.amazonaws.com/{unique_key}"
         
        presigned_data = s3.generate_presigned_post(
            Bucket=os.environ['S3_BUCKET_NAME'],
            Key=unique_key,
            Fields={
                # "acl": "public-read",
                "Content-Type": file_type
            },
            Conditions=[
                # {"acl": "public-read"},
                {"Content-Type": file_type}
            ],
            ExpiresIn=300
        )
        
        # DEBUG: Presigned data logging removed for security
        # return jsonify(presigned_data)
        return jsonify({
            'url': presigned_data['url'],
            'fields': presigned_data['fields'],
            'file_url': file_url  # Make sure this is included
        })
        
    except Exception as e:
        print(f"ERROR: {str(e)}")  # 👈 Log errors
        return jsonify({'error': str(e)}), 500
    
@profile_bp.route('/save-photo', methods=['POST'])
@login_required
def save_photo():
    user_id = session['user_id']
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    photo_url = request.json.get('photo_url')
    if not photo_url:
        return {'error': 'Missing photo URL'}, 400

    _, err = ProfileController.save_photo_url(user_id, photo_url)
    if err:
        return {'error': err}, 400

    return {'message': 'Photo saved successfully'}, 200

@profile_bp.route('/request-role-change', methods=['POST'])
@login_required
def request_role_change():
    user_id = session['user_id']
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    user, err = ProfileController.request_role_change(user_id)
    if err:
            flash("Role change not allowed for your account type.", "warning")
    else:
            if user.pending_role == 'escort':
                flash("Role change request submitted: seeker ➔ escort. Awaiting admin approval.", "info")
            else:
                flash("Role change request submitted: escort ➔ seeker. Awaiting admin approval.", "info")
    
    return redirect(url_for('profile.profile'))



@profile_bp.route('/deactivate', methods=['POST'])
@login_required
def deactivate_profile():
    user_id = session['user_id']
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    user, err = ProfileController.deactivate_user(user_id)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('profile.profile'))

    session.clear()
    flash("Your account has been deactivated. You are now logged out.", "info")
    return redirect(url_for('auth.auth', mode='login'))

@profile_bp.route('/my-ratings', methods=['POST'])
@login_required
def view_rating():
    return redirect(url_for('rating.my_ratings'))

@profile_bp.route('my-reports', methods=['POST'])
@login_required
def view_report():
    return redirect(url_for('report.my_reports'))
