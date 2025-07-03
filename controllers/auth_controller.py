from entities.user import User
from data_sources.user_repository import UserRepository

class AuthController:
    def __init__(self, db_connection):
        self.user_repository = UserRepository(db_connection)
        self._ensure_default_user_exists()

    def _ensure_default_user_exists(self):
        """Create default user if it doesn't exist in database"""
        default_user = self.user_repository.get_user_by_email("user@example.com")
        if not default_user:
            default_user = User("user@example.com", "securepassword")
            self.user_repository.save_user(default_user)

    def authenticate(self, email, password):
        """Authenticate user with email and password"""
        if not email or not password:
            return False
            
        user = self.user_repository.get_user_by_email(email)
        if user and user.check_password(password):
            return True
        return False

    def register(self, email, password):
        """Register new user with Argon2id hashed password"""
        if not email or not password:
            return False
            
        # Check if user already exists
        existing_user = self.user_repository.get_user_by_email(email)
        if existing_user:
            return False

        # Create new user and save to database
        try:
            new_user = User(email, password)
            return self.user_repository.save_user(new_user)
        except Exception:
            return False
    
    def get_user_by_email(self, email):
        """Get user by email address"""
        if not email:
            return None
        return self.user_repository.get_user_by_email(email)
    
    def user_exists(self, email):
        """Check if user exists by email"""
        if not email:
            return False
        user = self.user_repository.get_user_by_email(email)
        return user is not None
    
    def get_user_count(self):
        """Get total number of registered users"""
        try:
            return self.user_repository.user_count()
        except Exception:
            return 0
    
    def validate_email_format(self, email):
        """Basic email validation"""
        if not email or '@' not in email:
            return False
        parts = email.split('@')
        if len(parts) != 2:
            return False
        if not parts[0] or not parts[1]:
            return False
        if '.' not in parts[1]:
            return False
        return True
    
    def validate_password_strength(self, password):
        """Basic password strength validation"""
        if not password:
            return False, "Password is required"
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if len(password) > 128:
            return False, "Password must be less than 128 characters"
        return True, "Password is valid"
    
    def register_with_validation(self, email, password, confirm_password):
        """Register user with comprehensive validation"""
        # Email validation
        if not self.validate_email_format(email):
            return False, "Invalid email format"
        
        # Password validation
        is_valid, message = self.validate_password_strength(password)
        if not is_valid:
            return False, message
        
        # Password confirmation
        if password != confirm_password:
            return False, "Passwords do not match"
        
        # Check if user already exists
        if self.user_exists(email):
            return False, "Email already registered"
        
        # Register user
        success = self.register(email, password)
        if success:
            return True, "Account created successfully"
        else:
            return False, "Registration failed. Please try again"