
from blueprint.models import Profile, User, db
from blueprint.audit_log import log_event

class ProfileController:
    @staticmethod
    def get_profile_by_user_id(user_id):
        return Profile.query.filter_by(user_id=user_id).first()
 
    @staticmethod
    def update_profile(user_id, name=None, bio=None, availability=None, photo_url=None):
        profile = ProfileController.get_profile_by_user_id(user_id)
        if not profile:
            return None, "Profile not found"

        if name: profile.name = name
        if bio: profile.bio = bio
        if availability: profile.availability = availability
        if photo_url: profile.photo = photo_url

        db.session.commit()
        return profile, None

    @staticmethod
    def save_photo_url(user_id, photo_url):
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return None, "Profile not found"
        profile.photo = photo_url
        db.session.commit()
        return profile, None

    @staticmethod
    def request_role_change(user_id):
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"
        if user.role == 'seeker':
            user.pending_role = 'escort'
        elif user.role == 'escort':
            user.pending_role = 'seeker'
        else:
            return None, "Invalid role"

        db.session.commit()
        log_event(
			user_id,
			'role change request',
			f"User {user.email} requested role change: {user.role} ➔ {user.pending_role}. Awaiting admin approval."
        )
        return user, None

    @staticmethod
    def deactivate_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"
        user.activate = False
        db.session.commit()
        log_event(user_id, 'deactivate', f"User {user.email} deactivated their account.")
        return user, None