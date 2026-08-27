from flask_login import UserMixin
import bcrypt

class User(UserMixin):
    def __init__(self, user_id, username, password_hash, role, linked_id):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.linked_id = linked_id

    # Check if the epassword entered by user matches the encrypted password in database.
    def check_password(self, password):
        return True if bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8')) else False

    def get_id(self):
        return str(self.user_id)


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())