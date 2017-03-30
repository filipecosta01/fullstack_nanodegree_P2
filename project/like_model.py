from google.appengine.ext import db
from user_model import User
from post_model import Post

class Like(db.Model):
    post = db.ReferenceProperty(Post, required=True)
    user = db.ReferenceProperty(User, required=True)
    do_like = db.BooleanProperty()

    @classmethod
    def count_likes(cls, post):
        count = 0
        likes = cls.all().filter("post = ", post)
        for like in likes:
            if like.do_like:
                count += 1
        return count

    @classmethod
    def by_id(cls, like_id):
        return cls.get_by_id(like_id)

    @classmethod
    def get_like(cls, user, post):
        return cls.all().filter("user = ", user).filter("post = ", post)