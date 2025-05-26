from entities.user import User


class AuthController:
    def __init__(self):
        self.users = [User("user@example.com", "securepassword")]

    def authenticate(self, email, password):
        for user in self.users:
            if user.email == email and user.check_password(password):
                return True
        return False

    def register(self, email, password):
        # Check if user already exists
        if any(user.email == email for user in self.users):
            # Registration failed: user exists.
            return False

        # Create new user
        new_user = User(email, password)
        self.users.append(new_user)
        return True
