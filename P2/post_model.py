from google.appengine.ext import db

from user_model import User

class Post(db.Model):
    user = db.ReferenceProperty(User, required=True)
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def by_id(cls, post_id):
        return cls.get_by_id(post_id)

    @classmethod
    def get_all(cls):
        return cls.all().order("-created")