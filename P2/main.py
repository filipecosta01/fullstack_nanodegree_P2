# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import jinja2
import webapp2
import utils
from auth import *
from user_model import User
from post_model import Post
from comment_model import Comment
from like_model import Like

import time

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Handler(webapp2.RequestHandler):
    def __init__(self, request, response):
        self.initialize(request, response)

        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

    def write(self, *a, **kwargs):
        """
        TODO
        """
        self.response.out.write(*a, **kwargs)

    def render_str(self, template, **params):
        """
        TODO
        """
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kwargs):
        """
        TODO
        """
        self.write(self.render_str(template, **kwargs))

    def set_secure_cookie(self, name, val):
        """
        TODO
        """
        cookie_val = utils.make_secure_val(val)
        self.response.headers.add_header(
            "Set-Cookie",
            "%s=%s; Path=/" %(name, cookie_val)
        )

    def read_secure_cookie(self, name):
        """
        TODO
        """
        cookie_val = self.request.cookies.get(name)
        return cookie_val and utils.check_secure_val(cookie_val)

    def login(self, user):
        """
        TODO
        """
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        """
        TODO
        """
        self.response.headers.add_header("Set-Cookie", "user_id=; Path=/")

    def initialize(self, *a, **kwargs):
        """
        TODO
        """
        webapp2.RequestHandler.initialize(self, *a, **kwargs)

class LogoutHandler(Handler):
    """
    TODO: documentation
    """
    def get(self):
        """
        TODO: documentation
        """
        self.logout()
        self.redirect("/signup")

class LoginHandler(Handler):
    """
    TODO: documentation
    """
    def get(self):
        """
        TODO: documentation
        """
        self.render("login.html")
    def post(self):
        """
        TODO: documentation
        """
        input_username = self.request.get("username")
        input_password = self.request.get("password")

        params = dict(username=input_username)
        error = False
        if not input_username:
            params['invalid_username'] = "Username must be filled"
            error = True
        if not input_password:
            params['invalid_password'] = "Password must be filled"
            error = True

        if error:
            self.render("login.html", **params)
            return

        user = User.by_name(input_username)
        if user:
            if utils.check_valid_pw(user.username, input_password, user.pw_hash):
                self.login(user)

                self.redirect("/welcome")
                return
            else:
                params["invalid_username"] = "Invalid login | password"
                self.render("login.html", **params)

                return

        else:
            params["invalid_username"] = "Invalid login"
            self.render("login.html", **params)



class WelcomeHandler(Handler):
    """
    TODO: documentation
    """
    def get(self):
        """
        TODO: documentation
        """
        if self.user:
            self.render("welcome.html", username=self.user.username)
        else:
            self.redirect('/signup')

class SignupHandler(Handler):
    """
    TODO: documentation
    """
    def get(self):
        """
        TODO: documentation
        """
        self.render("signup.html", username="", password="",
                    verify="", email="", invalid_username="",
                    invalid_password="", invalid_verify="", invalid_email="",
                    not_match=""
                   )
    def post(self):
        """
        TODO: documentation
        """
        input_username = self.request.get("username")
        input_password = self.request.get("password")
        input_verify = self.request.get("verify")
        input_email = self.request.get("email")

        params = dict(
            username=input_username,
            email=input_email
        )

        valid_username = verify_username(input_username)
        valid_password = verify_password(input_password)
        valid_email = verify_email(input_email)
        match = verify_match(input_password, input_verify)
        error = False

        if not valid_username:
            params['invalid_username'] = "That's not a valid username"
            error = True
        else:
            if User.by_name(input_username):
                params['invalid_username'] = "That user already exists."
                error = True

        if not valid_password:
            params['invalid_password'] = "That wasn't a valid password."
            error = True

        if not match:
            params['not_match'] = "Your password didn't match."
            error = True

        if not valid_email:
            params['invalid_email'] = "That's not a valid email."
            error = True

        if error:
            self.render("signup.html", **params)
        else:
            encrypted_password = utils.make_pw_hash(input_username, input_password)
            user = User(
                username=input_username, pw_hash=encrypted_password, email=input_email)
            user.put()

            self.set_secure_cookie("user_id", str(user.key().id()))

            self.redirect("/welcome")

class BlogMainPosts(Handler):
    def get(self, posts = ""):
        posts = list(Post.get_all())

        self.render("blog.html", user=self.user, posts=posts)

class BlogNewPost(Handler):
    def get(self):
        self.render("new_post.html", user=self.user)

    def post(self):
        input_subject = self.request.get("subject")
        input_content = self.request.get("content")

        if not (input_subject and input_content):
            error_message = "Please inform subject and content"
            self.render("new_post.html",
                        error_message=error_message,
                        subject=input_subject, content=input_content
                       )
        else:
            post = Post(subject=input_subject, content=input_content, user=self.user)
            post.put()
            post_id = post.key().id()
            self.redirect("/blog/post/%s" % post_id)

class BlogShowPost(Handler):
    def get(self, post_id):
        if post_id and post_id.isdigit():
            post = Post.by_id(int(post_id))
            if not post:
                self.error(404)
                return
            comments = list(Comment.get_all(post))

            self.render("single_post.html", user=self.user, post=post, comments=comments)
        else:
            self.error(404)
            return

    def post(self, post_id):
        post = Post.by_id(int(post_id))
        input_comment = self.request.get("comment")
        comment_error = False

        comments = Comment.get_all(post)

        if not input_comment:
            comment_error = True
            return self.render("single_post.html",
                               user=self.user, post=post, comments=comments,
                               comment_error=comment_error
                              )

        comment = Comment(comment=input_comment, user=self.user, post=post)
        comment.put()

        time.sleep(0.5)

        self.redirect("/blog/post/%s" % post_id)

class BlogEditPost(Handler):
    def get(self, post_id):
        if post_id:
            post = Post.by_id(int(post_id))
            if not post:
                return self.render("error_page.html", error="Post does not exists")
            if not (self.user and post.user.key().id() == self.user.key().id()):
                return self.render("error_page.html", error="You are not the owner of this post")

            return self.render("edit_post.html", user=self.user, subject=post.subject,
                               content=post.content, post=post)
        else:
            return self.render("error_page.html", error="The post does not exists")

    def post(self, post_id):
        input_subject = self.request.get("subject")
        input_content = self.request.get("content")

        if not (input_subject and input_content):
            error_message = "Please inform subject and content"
            self.render("edit_post.html",
                        error_message=error_message,
                        subject=input_subject, content=input_content,
                        post=post
                       )
        else:
            post = Post.by_id(int(post_id))
            post.subject = input_subject
            post.content = input_content
            post.put()

            post_id = post.key().id()
            self.redirect("/blog/post/%s"%post_id)

class BlogEditComment(Handler):
    def get(self, comment_id):
        if comment_id:
            comment = Comment.by_id(int(comment_id))
            if not comment:
                return self.render("error_page.html", error="Comment does not exists")
            if not (self.user and comment.user.key().id() == self.user.key().id()):
                return self.render("error_page.html", error="You are not the owner of this comment")

            return self.render("single_comment.html", user=self.user, comment=comment)
        else:
            return self.render("error_page.html", error="The comment does not exists")

    def post(self, comment_id):
        input_comment = self.request.get("comment")
        comment = Comment.by_id(int(comment_id))

        if not input_comment:
            comment_error = True
            return self.render("single_comment.html", user=self.user, comment=comment,
                               comment_error=comment_error)
        comment.comment = input_comment
        comment.put()

        time.sleep(0.5)

        return self.redirect("/blog/post/%s" %comment.post.key().id())

class BlogDeleteComment(Handler):
    def post(self, comment_id):
        comment = Comment.by_id(int(comment_id))

        if comment.user.key().id() == self.user.key().id():
            comment.delete()

            time.sleep(0.5)

            return self.redirect("/blog/post/%s" % comment.post.key().id())
        else:
            return self.redirect("/blog/post/%s" % comment.post.key().id(), error=True)

class BlogError(Handler):
    def get(self, error=""):
        if not error:
            return self.render("error_page.html",
                               error="Something wrong happened or an invalid action was dispatched."
                              )

        self.render("error_page.html", error=error)


app = webapp2.WSGIApplication([
    ('/signup', SignupHandler),
    ('/welcome', WelcomeHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/blog', BlogMainPosts),
    ('/blog/post/new', BlogNewPost),
    ('/blog/post/([0-9]+)', BlogShowPost),
    ('/blog/post/edit/([0-9]+)', BlogEditPost),
    ('/blog/comment/edit/([0-9]+)', BlogEditComment),
    ('/blog/comment/delete/([0-9]+)', BlogDeleteComment),
    ('/error', BlogError)
], debug=True)
