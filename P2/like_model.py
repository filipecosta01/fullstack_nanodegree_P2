from google.appengine.ext import db
from user_model import User
from post_model import Post

class Like(db.Model):
    post = db.ReferenceProperty(Post, required=True)
    user = db.ReferenceProperty(User, required=True)

    @classmethod
    def can_like(cls, user_id, post_id):
        return cls.all().filter("post = ", post_id).filter("user = ", user_id).get() != None

    @classmethod
    def count_likes(cls, post_id):
        count = 0
        likes = cls.all().filter("post = ", post_id).get()
        for like in likes:
          count += 1
        return count

    @classmethod
    def by_id(cls, post_id):
        return cls.get_by_id(post_id)