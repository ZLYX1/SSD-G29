import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from blueprint.models import Profile
from extensions import db
from blueprint.decorators import login_required
# from flask_wtf import CSRFProtect
from extensions import db, csrf, s3
from datetime import datetime
from flask import jsonify

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

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
    
    
@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def profile():
	user_profile = Profile.query.filter_by(user_id=session['user_id']).first()

	if request.method == 'POST':
		user_profile.name = request.form.get('name')
		user_profile.bio = request.form.get('bio')
		user_profile.availability = request.form.get('availability')

		photo_url = request.form.get('photo_url')
		if photo_url:
			user_profile.photo = photo_url

		db.session.commit()
		flash("Profile updated successfully!", "success")
		return redirect(url_for('profile.profile'))

	return render_template('profile.html', profile=user_profile)

# @profile_bp.route('/generate-presigned-url', methods=['POST'])
# @login_required
# def generate_presigned_url():
# 	print("\n=== Received request for presigned URL ===")
# 	print("Request headers:", request.headers)
# 	print("Request JSON:", request.json)
    
# 	if not request.is_json:
# 		print("Error: Request is not JSON")
# 		return jsonify({'error': 'Request must be JSON'}), 400
        
# 	# print("generate_presignurl")
# 	file_name = request.json.get('file_name')
# 	file_type = request.json.get('file_type')
# 	S3_BUCKET = os.environ['S3_BUCKET_NAME']

# 	if not file_name or not file_type:
# 		return {'error': 'Missing file name or type'}, 400

# 	allowed_types = ["image/jpeg", "image/png", "image/jpg"]
# 	if file_type not in allowed_types:
# 		return {'error': 'Invalid file type'}, 400


# 	try:
# 		ext = file_name.split('.')[-1]
# 		unique_filename =   datetime.utcnow().strftime("%Y%m%d%H%M%S")
# 		key = f"profile_photos/{session['user_id']}/{unique_filename}.{ext}"
# 		presigned_post = s3.generate_presigned_post(
# 			Bucket=S3_BUCKET,
# 			Key=key,
# 			# Fields={"Content-Type": file_type},
# 			# Conditions=[{"Content-Type": file_type}],
   
#             # Fields={},  # no Content-Type
#             # Conditions=[],  # no Content-Type
#             Fields={
#                 "acl": "public-read",
#                 "Content-Type": file_type
#             },
#             Conditions=[
#                 {"acl": "public-read"},
#                 {"Content-Type": file_type}
#             ],
# 			ExpiresIn=300
# 		)
# 		file_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{key}"
# 		return jsonify({
#             'url': presigned_post['url'],
#             'fields': presigned_post['fields'],
#             'file_url': file_url
#         })
# 		# return jsonify(presigned_post)
# 	except Exception as e:
# 		print(f"Exception in generate_presigned_url: {e}")
# 		return jsonify({'error': str(e)}), 500

@profile_bp.route('/generate-presigned-url', methods=['POST'])
@login_required
def generate_presigned_url():
    try:
        file_name = request.json.get('file_name')
        file_type = request.json.get('file_type')
        
        print(f"DEBUG: Generating presigned URL for {file_name} ({file_type})")  # 👈 Log input
        
        if not file_name or not file_type:
            return jsonify({'error': 'Missing file name or type'}), 400

        # Generate a unique filename to avoid collisions
        import uuid
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
        
        print(f"DEBUG: Presigned data: {presigned_data}")  # 👈 Log output
        # return jsonify(presigned_data)
        return jsonify({
            'url': presigned_data['url'],
            'fields': presigned_data['fields'],
            'file_url': file_url  # Make sure this is included
        })
        
    except Exception as e:
        print(f"ERROR: {str(e)}")  # 👈 Log errors
        return jsonify({'error': str(e)}), 500
    
@csrf.exempt
@profile_bp.route('/save-photo', methods=['POST'])
@login_required
def save_photo():
    print("save photo to db!!")
    photo_url = request.json.get('photo_url')
    if not photo_url:
        return {'error': 'Missing photo URL'}, 400

    user_profile = Profile.query.filter_by(user_id=session['user_id']).first()
    user_profile.photo = photo_url  # or just the filename if preferred
    db.session.commit()

    return {'message': 'Photo saved successfully'}, 200