# pymodules/auth.py
# Copyright (c) 2026 Banshee (https://www.banshee.pro)
# License: AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

import bcrypt
from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

    @staticmethod
    def get(user_id):
        from config import load_conf
        conf = load_conf()
        if user_id == "1" and conf.get("auth_username"):
            return User("1", conf["auth_username"])
        return None

    @staticmethod
    def authenticate(username, password):
        from config import load_conf

        conf = load_conf()

        stored_username = conf.get("auth_username")
        stored_hash = conf.get("auth_password_hash")

        if not stored_username or not stored_hash:
            return None

        if username != stored_username:
            return None

        try:
            if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
                return User("1", username)
        except Exception:
            return None

        return None


def generate_password_hash(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
