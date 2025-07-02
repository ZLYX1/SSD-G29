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
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # NEW FIELDS
    gender = db.Column(db.String(20), nullable=False)  # e.g. Male, Female, Non-binary
    
    # Email verification fields
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verification_token = db.Column(db.String(100), unique=True, nullable=True)
    email_verification_token_expires = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    profile = db.relationship('Profile', backref='user', uselist=False, cascade="all, delete-orphan")
    bookings_made = db.relationship('Booking', foreign_keys='Booking.seeker_id', backref='seeker', lazy='dynamic')
    bookings_received = db.relationship('Booking', foreign_keys='Booking.escort_id', backref='escort', lazy='dynamic')
    time_slots = db.relationship('TimeSlot', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    photo = db.Column(db.String(100), default='default.jpg')
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
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False, unique=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    booking = db.relationship('Booking', backref=db.backref('rating', uselist=False))
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='ratings_given')
    reviewed = db.relationship('User', foreign_keys=[reviewed_id], backref='ratings_received')
    
    def __repr__(self):
        return f'<Rating {self.rating}/5 for booking {self.booking_id}>'