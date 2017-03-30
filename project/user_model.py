"""
User Model for database.
"""
from google.appengine.ext import db

class User(db.Model):
    """
    The User instance contains an username, a hashed and non-parseable password
    and optionally an e-mail.
    """
    username = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty(required=False)

    @classmethod
    def by_name(cls, username):
        """
        Get from dabatase an user with the username passed in parameter.
        """
        user = cls.all().filter('username =', username).get()
        return user

    @classmethod
    def by_id(cls, user_id):
        """
        Get from dabatase an user with the id passed in parameter.
        """
        return cls.get_by_id(user_id)

    @classmethod
    def register(cls, username, password, email=None):
        """
        Create a new instance of the User with a hashed password.
        """
        pw_hash = utils.make_pw_hash(username, password)
        return cls(username=username, pw_hash=pw_hash, email=email)
