class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def check_password(self, password):
        return self.password == password
  
# main branch original  
# from argon2 import PasswordHasher
# from argon2.exceptions import VerifyMismatchError

# class User:
#     def __init__(self, email, password, user_id=None):
#         self.id = user_id
#         self.email = email
#         self.password_hash = self._hash_password(password)
    
#     def _hash_password(self, password):
#         ph = PasswordHasher(
#             memory_cost=19456,
#             time_cost=2,
#             parallelism=1,
#             hash_len=32,
#             salt_len=16
#         )
#         return ph.hash(password)
    
#     def check_password(self, password):
#         try:
#             ph = PasswordHasher(
#                 memory_cost=19456,
#                 time_cost=2,
#                 parallelism=1,
#                 hash_len=32,
#                 salt_len=16
#             )
#             ph.verify(self.password_hash, password)
#             return True
#         except VerifyMismatchError:
#             return False
#         except Exception:
#             return False  # Fail silently for security
    
#     @classmethod
#     def create_with_stored_data(cls, user_id, email, password_hash):
#         user = cls.__new__(cls)
#         user.id = user_id
#         user.email = email
#         user.password_hash = password_hash
#         return user