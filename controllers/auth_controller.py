from entities.user import User


class AuthController:
    def __init__(self):
        self.users = [User("user@example.com", "securepassword")]

    def authenticate(self, email, password):
        for user in self.users:
            if user.email == email and user.check_password(password):
                return True
        return False
