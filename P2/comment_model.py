from google.appengine.ext import db
from user_model import User
from post_model import Post

class Comment(db.Model):
    comment = db.TextProperty(required = True)
    user = db.ReferenceProperty(User, required=True)
    post = db.ReferenceProperty(Post, required=True)
    created = db.DateTimeProperty(auto_now_add = True)

    @classmethod
    def by_id(cls, comment_id):
      return cls.get_by_id(comment_id)

    @classmethod
    def get_all(cls, post):
        return cls.all().filter("post = ", post.key()).order("-created")