class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def check_password(self, password):
        return self.password == password
