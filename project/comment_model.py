"""
Comment Model for database.
"""

from google.appengine.ext import db
from user_model import User
from post_model import Post

class Comment(db.Model):
    """
    The Comment instance contains an user that made the comment,
    a post where the comment was made and the string comment itself.
    """
    comment = db.TextProperty(required=True)
    user = db.ReferenceProperty(User, required=True)
    post = db.ReferenceProperty(Post, required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def by_id(cls, comment_id):
        """
        Get from dabatase a comment with the id passed in parameter.
        """
        return cls.get_by_id(comment_id)

    @classmethod
    def get_all(cls, post):
        """
        Get all comments dabatase a comment with the post passed in parameter.
        """
        return cls.all().filter("post = ", post.key()).order("-created")
