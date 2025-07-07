# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

from extensions import db  # ✅ Correct place to import from
# db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # password_hash = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(10), nullable=False, default='seeker') # 'seeker', 'escort', 'admin'
    # for otp verification [if failed]
    active = db.Column(db.Boolean, default=True, nullable=False)
    # for user to deactivate acc
    activate = db.Column(db.Boolean, default=True, nullable=False)
    # admin soft delete
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # NEW FIELDS
    gender = db.Column(db.String(20), nullable=False)  # e.g. Male, Female, Non-binary
    # For role change requests
    pending_role = db.Column(db.String(10), nullable=True)  # e.g. 'seeker' or 'escort'
    
    # Email verification fields
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verification_token = db.Column(db.String(100), unique=True, nullable=True)
    email_verification_token_expires = db.Column(db.DateTime, nullable=True)
    
    # Phone verification fields (OTP System)
    phone_number = db.Column(db.String(20), nullable=True)  # Phone number for OTP
    phone_verified = db.Column(db.Boolean, default=False, nullable=False)
    otp_code = db.Column(db.String(6), nullable=True)  # 6-digit OTP code
    otp_expires = db.Column(db.DateTime, nullable=True)  # OTP expiration time
    otp_attempts = db.Column(db.Integer, default=0, nullable=False)  # Failed OTP attempts
    
    # Password security fields (Password History & Expiration)
    password_created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    password_expires_at = db.Column(db.DateTime, nullable=True)  # When password expires
    password_change_required = db.Column(db.Boolean, default=False, nullable=False)  # Force password change
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)  # Track failed logins
    account_locked_until = db.Column(db.DateTime, nullable=True)  # Account lockout timestamp
    
    # Relationships
    profile = db.relationship('Profile', backref='user', uselist=False, cascade="all, delete-orphan")
    password_history = db.relationship('PasswordHistory', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    # bookings_made = db.relationship('Booking', foreign_keys='Booking.seeker_id', backref='seeker', lazy='dynamic')

    # bookings_received = db.relationship('Booking', foreign_keys='Booking.escort_id', backref='escort', lazy='dynamic')
    time_slots = db.relationship('TimeSlot', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    
    bookings_made = db.relationship('Booking', foreign_keys='Booking.seeker_id', back_populates='seeker', lazy='dynamic')
    bookings_received = db.relationship('Booking', foreign_keys='Booking.escort_id', back_populates='escort', lazy='dynamic')

    def set_password(self, password, password_expiry_days=90, check_history=True):
        # Check password history if requested (skip for new users)
        if check_history and self.id:
            if self.is_password_in_history(password):
                return False, "Password has been used recently. Please choose a different password."
        
        # Store old password in history before updating (if user exists)
        if self.id and self.password_hash:
            self.add_password_to_history(self.password_hash)
        
        self.password_hash = generate_password_hash(password)
        self.password_created_at = datetime.datetime.utcnow()
        
        # Set expiration date
        if password_expiry_days > 0:
            self.password_expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=password_expiry_days)
        else:
            self.password_expires_at = None
            
        # Reset security flags
        self.password_change_required = False
        self.failed_login_attempts = 0
        self.account_locked_until = None
        
        return True, "Password updated successfully."
    
    def add_password_to_history(self, password_hash):
        """Add current password to password history"""
        try:
            history_entry = PasswordHistory(
                user_id=self.id,
                password_hash=password_hash,
                created_at=datetime.datetime.utcnow()
            )
            db.session.add(history_entry)
            # Keep only last 5 passwords in history
            old_entries = self.password_history.order_by(PasswordHistory.created_at.desc()).offset(5).all()
            for entry in old_entries:
                db.session.delete(entry)
        except Exception as e:
            # If there's an error with password history, don't fail the password update
            print(f"Warning: Could not add password to history: {e}")
    
    def is_password_in_history(self, password, limit=5):
        """Check if password exists in user's password history"""
        # For new users or users not in session, skip history check
        if not self.id or not db.session.object_session(self):
            return False
            
        try:
            history_entries = self.password_history.order_by(PasswordHistory.created_at.desc()).limit(limit).all()
        except:
            # If there's an issue with the relationship query, skip history check
            return False
        
        # Check current password
        if self.password_hash and check_password_hash(self.password_hash, password):
            return True
            
        # Check password history
        for entry in history_entries:
            if check_password_hash(entry.password_hash, password):
                return True
        return False
    
    def is_password_expired(self):
        """Check if user's password has expired"""
        if not self.password_expires_at:
            return False
        return datetime.datetime.utcnow() > self.password_expires_at
    
    def days_until_password_expires(self):
        """Get number of days until password expires"""
        if not self.password_expires_at:
            return None
        delta = self.password_expires_at - datetime.datetime.utcnow()
        return max(0, delta.days)
    
    def is_account_locked(self):
        """Check if account is currently locked due to failed login attempts"""
        if not self.account_locked_until:
            return False
        return datetime.datetime.utcnow() < self.account_locked_until
    
    def increment_failed_login(self, max_attempts=5, lockout_duration_minutes=30):
        """Increment failed login attempts and lock account if necessary"""
        self.failed_login_attempts += 1
        
        if self.failed_login_attempts >= max_attempts:
            self.account_locked_until = datetime.datetime.utcnow() + datetime.timedelta(minutes=lockout_duration_minutes)
            return f"Account locked for {lockout_duration_minutes} minutes due to too many failed login attempts."
        
        attempts_left = max_attempts - self.failed_login_attempts
        return f"Invalid credentials. {attempts_left} attempts remaining before account lockout."
    
    def reset_failed_logins(self):
        """Reset failed login attempts and unlock account"""
        self.failed_login_attempts = 0
        self.account_locked_until = None
    
    def is_available(self):
        """Check if user account is available (not deleted and active)"""
        return not self.deleted and self.active
    
    def get_display_name(self):
        """Get display name for user - shows 'Deleted User' if account is deleted"""
        if self.deleted:
            return "Deleted User"
        return self.profile.name if self.profile else self.email.split('@')[0]
    
    def check_password(self, password):
        """Enhanced password checking with security features"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'


class PasswordHistory(db.Model):
    """Track user password history to prevent reuse"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f'<PasswordHistory {self.id} for User {self.user_id}>'

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    photo = db.Column(db.String(2000), default='default.jpg')
    availability = db.Column(db.String(50), default='Available')
    rating = db.Column(db.Float)
    age = db.Column(db.Integer)
    preference = db.Column(db.String(50), nullable=True)  # e.g. Interested in: Men, Women, Both

class TimeSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seeker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    escort_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)  # Booking start time
    end_time = db.Column(db.DateTime, nullable=False)    # Booking end time
    status = db.Column(db.String(20), default='Pending', nullable=False)  # 'Pending', 'Confirmed', 'Rejected'
    
    # booking_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False) # 'Pending', 'Confirmed', 'Rejected'
    # seeker = db.relationship('User', foreign_keys=[seeker_id])
    # escort = db.relationship('User', foreign_keys=[escort_id])
    # seeker = db.relationship('User', foreign_keys=[seeker_id], back_populates='bookings_made')
    # escort = db.relationship('User', foreign_keys=[escort_id], back_populates='bookings_received')
    seeker = db.relationship('User', foreign_keys=[seeker_id], back_populates='bookings_made')
    escort = db.relationship('User', foreign_keys=[escort_id], back_populates='bookings_received')
    def __repr__(self):
        return f'<Booking {self.id} escort:{self.escort_id} seeker:{self.seeker_id} from {self.start_time} to {self.end_time}>'
    
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Completed', nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reported_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Enhanced reporting fields
    report_type = db.Column(db.String(50), nullable=False)  # 'inappropriate_behavior', 'harassment', 'fraud', etc.
    title = db.Column(db.String(200), nullable=False)  # Brief title of the report
    description = db.Column(db.Text, nullable=False)  # Detailed description
    evidence_urls = db.Column(db.Text)  # JSON array of evidence URLs/screenshots
    severity = db.Column(db.String(20), default='Medium', nullable=False)  # 'Low', 'Medium', 'High', 'Critical'
    
    # Status tracking
    status = db.Column(db.String(30), default='Pending Review', nullable=False)  # 'Pending Review', 'Under Investigation', 'Resolved', 'Dismissed'
    admin_notes = db.Column(db.Text)  # Admin notes for investigation
    resolution = db.Column(db.Text)  # Resolution details
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Admin who handled the report
    assigned_admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='reports_made')
    reported = db.relationship('User', foreign_keys=[reported_id], backref='reports_received')
    assigned_admin = db.relationship('User', foreign_keys=[assigned_admin_id], backref='reports_handled')
    
    def __repr__(self):
        return f'<Report {self.id}: {self.report_type} against User {self.reported_id}>'
    
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    # Optional: soft delete / system flag
    deleted_by_sender = db.Column(db.Boolean, default=False)
    deleted_by_recipient = db.Column(db.Boolean, default=False)

    # Relationships (reverse navigation)
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    
    def __repr__(self):
        return f'<Message from {self.sender_id} to {self.recipient_id}>'

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    booking = db.relationship('Booking', backref=db.backref('rating', uselist=False))
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='ratings_given')
    reviewed = db.relationship('User', foreign_keys=[reviewed_id], backref='ratings_received')

    __table_args__ = (
        db.UniqueConstraint('booking_id', 'reviewer_id', name='unique_booking_reviewer'),
    )
    
    def __repr__(self):
        return f'<Rating {self.rating}/5 for booking {self.booking_id}>'
    
# // To test
class Favourite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    favourite_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Optional relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='favourites_given')
    favourited_user = db.relationship('User', foreign_keys=[favourite_user_id], backref='favourites_received')

    def __repr__(self):
        return f"<Favourite by {self.user_id} → {self.favourite_user_id}>"
    
class AuditLog(db.Model):
    __tablename__ = 'audit_log'  # explicit table name for clarity
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationship back to User
    user = db.relationship('User', backref='audit_logs')

    def __repr__(self):
        return f"<AuditLog {self.id} {self.action} by {self.user_id}>"
