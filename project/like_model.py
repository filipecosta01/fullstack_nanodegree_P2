"""
Like Model for database.
"""

from google.appengine.ext import db
from user_model import User
from post_model import Post

class Like(db.Model):
    """
    The Like instance contains an user that liked a post, a post liked and a control
    variable indication the status of the like itself.
    """
    post = db.ReferenceProperty(Post, required=True)
    user = db.ReferenceProperty(User, required=True)
    do_like = db.BooleanProperty()

    @classmethod
    def count_likes(cls, post):
        """
        Get the number of likes for a specific post from database and return
        the number of likes.
        """
        count = 0
        likes = cls.all().filter("post = ", post)
        for like in likes:
            if like.do_like:
                count += 1
        return count

    @classmethod
    def by_id(cls, like_id):
        """
        Get from dabatase a like with the id passed in parameter.
        """
        return cls.get_by_id(like_id)

    @classmethod
    def get_like(cls, user, post):
        """
        Get from dabatase a like with the user and post passed in parameter.
        """
        return cls.all().filter("user = ", user).filter("post = ", post)
