"""
User Model for database usage.
"""
from google.appengine.ext import db

class User(db.Model):
    username = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty(required=False)

    @classmethod
    def by_name(cls, username):
        """
        Search in dabatase an user with the username passed in parameter.
        """
        user = cls.all().filter('username =', username).get()
        return user

    @classmethod
    def by_id(cls, user_id):
        """
        Search in dabatase an user with the id passed in parameter.
        """
        return cls.get_by_id(user_id)

    @classmethod
    def register(cls, username, password, email=None):
        """
        """
        pw_hash = utils.make_pw_hash(username, password)
        return cls(
          username=username,
          pw_hash=pw_hash,
          email=email
        )