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
import time
import logging
import jinja2
import webapp2
import utils

# Authentication auxiliar functions
from auth import verify_username, verify_password, verify_email, verify_match

# Database models
from user_model import User
from post_model import Post
from comment_model import Comment
from like_model import Like

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    autoescape=True
)


class Handler(webapp2.RequestHandler):
    """
    Default webapp2 handler, all handlers must pass this default when
    instantiated.
    """
    def __init__(self, request, response):
        self.initialize(request, response)

        uid = self.read_secure_cookie("user_id")
        self.user = uid and User.by_id(int(uid))

    def write(self, *a, **kwargs):
        """
        Write in the content of a template *a the parameters **kwargs.
        """
        self.response.out.write(*a, **kwargs)

    def render_str(self, template, **params):
        """
        Render in a template the parameters **params.
        """
        template_page = JINJA_ENV.get_template(template)
        return template_page.render(params)

    def render(self, template, **kwargs):
        """
        Stub method to write in a page the content in parameters.
        """
        self.write(self.render_str(template, **kwargs))

    def set_secure_cookie(self, name, val):
        """
        Add to the response header the cookie with a name and value.
        """
        cookie_val = utils.make_secure_val(val)
        self.response.headers.add_header(
            "Set-Cookie",
            "%s=%s; Path=/" % (name, cookie_val)
        )

    def read_secure_cookie(self, name):
        """
        Read from the document the cookie stored.
        """
        cookie_val = self.request.cookies.get(name)
        return cookie_val and utils.check_secure_val(cookie_val)

    def login(self, user):
        """
        Set a cookie with the user_id after login/signup.
        """
        self.set_secure_cookie("user_id", str(user.key().id()))

    def logout(self):
        """
        Remove the cookie with the user_id after login/signup.
        """
        self.response.headers.add_header("Set-Cookie", "user_id=; Path=/")

    def initialize(self, *a, **kwargs):
        """
        Initialize method for the request handler.
        """
        webapp2.RequestHandler.initialize(self, *a, **kwargs)


class BlogMain(Handler):
    """
    Handler for the main page of the blog.
    """
    def get(self):
        """
        GET method for the / action.
        If user is authenticated, redirects to the blog main page.
        Otherwise goes to login page.
        """
        if self.user:
            self.redirect("/blog/posts")
        else:
            self.redirect("/login")


class LoginHandler(Handler):
    """
    Handler for the login page.
    """
    def get(self):
        """
        GET method for the /login action.
        If the user is authenticated, redirects to the main page of the blog.
        Otherwise, render the login page.
        """
        if self.user:
            return self.redirect("/blog/posts")
        self.render("login.html")

    def post(self):
        """
        POST method for the /login action.
        Verifies the user's input, check if an user exists with the
        credentials provided and redirects to the welcome page if yes,
        stay in the same page and show errors if no.
        """
        input_username = self.request.get("username")
        input_password = self.request.get("password")

        params = dict(username=input_username)
        error = False
        if not input_username:
            params["invalid_username"] = "Username must be filled"
            error = True
        if not input_password:
            params["invalid_password"] = "Password must be filled"
            error = True

        if error:
            self.render("login.html", **params)
            return

        user = User.by_name(input_username)
        if user:
            if utils.check_valid_pw(user.username, input_password,
                                    user.pw_hash):
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


class LogoutHandler(Handler):
    """
    Handler for the logout feature.
    """
    def get(self):
        """
        GET method for /logout action.
        Remove the cookie saved in browser with information about the user,
        plus redirects to the login page.
        """
        self.logout()
        self.redirect("/login")


class WelcomeHandler(Handler):
    """
    Handler for the welcome page.
    """
    def get(self):
        """
        GET method for /welcome action.
        Check if user is authenticated to show further instructions in the
        welcome page.
        If not, redirects to the login page.
        """
        if self.user:
            self.render("welcome.html", username=self.user.username)
        else:
            self.redirect("/login")


class SignupHandler(Handler):
    """
    Handler for the signup page.
    """
    def get(self):
        """
        GET method for /signup action.
        If user is authenticated, redirects to the blog main page.
        If not, render the signup page.
        """
        if self.user:
            return self.redirect("/blog/posts")

        return self.render("signup.html", username="", password="",
                           verify="", email="", invalid_username="",
                           invalid_password="", invalid_verify="",
                           invalid_email="", not_match="")

    def post(self):
        """
        POST method for the /signup action.
        Validates the inputs and redirects the user to the welcome page if
        validations are ok.
        If not, render the signup page, keeping the username and email values,
        and show error messages.
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
            params["invalid_username"] = "That's not a valid username"
            error = True
        else:
            if User.by_name(input_username):
                params["invalid_username"] = "That user already exists."
                error = True

        if not valid_password:
            params["invalid_password"] = "That wasn't a valid password."
            error = True

        if not match:
            params["not_match"] = "Your password didn't match."
            error = True

        if not valid_email:
            params["invalid_email"] = "That's not a valid email."
            error = True

        if error:
            self.render("signup.html", **params)

        else:
            encrypted_password = utils.make_pw_hash(input_username,
                                                    input_password)
            user = User(
                username=input_username, pw_hash=encrypted_password,
                email=input_email)
            user.put()

            self.set_secure_cookie("user_id", str(user.key().id()))

            self.redirect("/welcome")


class BlogMainPosts(Handler):
    """
    Handler for the blog's main page.
    """
    def get(self, posts=""):
        """
        GET method for /blog/posts action.
        Retrieve all the posts from database and render the main blog view.
        """
        posts = list(Post.get_all())

        self.render("blog.html", user=self.user, posts=posts)


class BlogNewPost(Handler):
    """
    Handler for the new post's page.
    """
    def get(self):
        """
        GET method for /blog/post/new action.
        Render the new post's page.
        """

        if not self.user:
            return self.redirect("/login")
        self.render("new_post.html", user=self.user)

    def post(self):
        """
        POST method for /blog/post/new action.
        Validates the inputs and redirects the user to the post page if
        validations are ok.
        If not, render the new post's page, keeping the field values, and
        show error messages.
        """

        if not self.user:
            return self.redirect("/login")

        input_subject = self.request.get("subject")
        input_content = self.request.get("content")

        if not (input_subject and input_content):
            error_message = "Please inform subject and content"
            self.render("new_post.html",
                        error_message=error_message,
                        subject=input_subject, content=input_content)
        else:
            post = Post(subject=input_subject, content=input_content,
                        user=self.user)
            post.put()
            post_id = post.key().id()
            self.redirect("/blog/post/%s" % post_id)


class BlogShowPost(Handler):
    """
    Handler for the show single post page.
    """
    def get(self, post_id):
        """
        GET method for /blog/post/<post_id> action.
        Render the post's page, plus comments and comment area.
        """
        if post_id and post_id.isdigit():
            post = Post.by_id(int(post_id))
            if not post:
                return self.render("error_page.html",
                                   error="Post does notexists")

            comments = list(Comment.get_all(post))

            like = Like.get_like(user=self.user, post=post).get()
            count_likes = Like.count_likes(post=post)

            self.render("show_post.html", user=self.user, post=post, like=like,
                        count_likes=count_likes, comments=comments)
        else:
            return self.render("error_page.html", error="Post does not exists")

    def post(self, post_id):
        """
        POST method for /blog/post/<post_id> action.
        Validates the inputs and redirects the user to the post page if
        validations are ok.
        If not, render the post's page, keeping the field values, and show
        error messages.
        """
        post = Post.by_id(int(post_id))
        input_comment = self.request.get("comment")
        comment_error = False

        comments = Comment.get_all(post)

        if not input_comment:
            comment_error = True
            return self.render("show_post.html",
                               user=self.user, post=post, comments=comments,
                               comment_error=comment_error)

        comment = Comment(comment=input_comment, user=self.user, post=post)
        comment.put()

        time.sleep(0.5)

        self.redirect("/blog/post/%s" % post_id)


class BlogEditPost(Handler):
    """
    Handler for the edit post's page.
    """
    def get(self, post_id):
        """
        GET method for /blog/post/edit/<post_id> action.
        Render the edit post's page.
        """

        if not self.user:
            return self.redirect("/login")
        if post_id:
            post = Post.by_id(int(post_id))
            if not post:
                return self.render("error_page.html",
                                   error="Post does notexists")
            if post.user.key().id() != self.user.key().id():
                return self.render("error_page.html",
                                   error="You are not the owner of this post")

            return self.render("edit_post.html", user=self.user,
                               subject=post.subject,
                               content=post.content, post=post)
        else:
            return self.render("error_page.html", error="Post does not exists")

    def post(self, post_id):
        """
        POST method for /blog/post/edit/<post_id> action.
        Validates the inputs and redirects the user to the post page if
        validations are ok.
        If not, render the edit post's page, keeping the field values, and
        show error messages.
        """

        if not self.user:
            return self.redirect("/login")

        input_subject = self.request.get("subject")
        input_content = self.request.get("content")

        post = Post.by_id(int(post_id))

        if not (input_subject and input_content):
            error_message = "Please inform subject and content"
            self.render("edit_post.html",
                        error_message=error_message,
                        subject=input_subject, content=input_content,
                        post=post)
        else:
            post.subject = input_subject
            post.content = input_content
            post.put()

            post_id = post.key().id()
            self.redirect("/blog/post/%s" % post_id)


class BlogDeletePost(Handler):
    """
    Handler for the delete post's action.
    """
    def post(self, post_id):
        """
        POST method for /blog/post/delete/<post_id> action.
        Validates the current user and if they can delete the post and remove
        it from database.
        """

        if not self.user:
            return self.redirect("/login")

        if post_id:
            post = Post.by_id(int(post_id))
            if not post:
                return self.render("error_page.html",
                                   error="Post does not exists")
            if post.user.key().id() != self.user.key().id():
                return self.render("error_page.html",
                                   error="You are not the owner of this post")

            post.delete()

            time.sleep(0.5)

            return self.redirect("/blog/posts")
        else:
            return self.render("error_page.html", error="Post does not exists")


class BlogLikePost(Handler):
    """
    Handler for the like post's action.
    """
    def post(self, post_id):
        """
        POST method for /blog/post/like/<post_id> action.
        Validates the current user and if they can like the post and insert
        a new like row on database.
        """

        if not self.user:
            return self.redirect("/login")

        post = Post.by_id(int(post_id))
        user = self.user
        if not post:
            error_message = "You can't like posts that does not exists"
            return self.render("error_page.html", error=error_message)
        else:
            like = Like.get_like(user=user, post=post).get()
            if post and post.user.key().id() == user.key().id():
                error_message = "You can't like your own posts"
                return self.render("error_page.html", error=error_message)
            if like and like.do_like:
                like.do_like = False
            elif like and not like.do_like:
                like.do_like = True
            else:
                like = Like(post=post, user=self.user, do_like=True)

            like.put()

            time.sleep(0.5)

            self.redirect("/blog/post/%s" % post_id)


class BlogEditComment(Handler):
    """
    Handler for the comment in posts action.
    """
    def get(self, comment_id):
        """
        GET method for /blog/comment/edit/<comment_id> action.
        Render the edit comments's page.
        """

        if not self.user:
            return self.redirect("/login")

        if comment_id:
            comment = Comment.by_id(int(comment_id))
            if not comment:
                return self.render("error_page.html",
                                   error="Comment does not exists")
            if comment.user.key().id() != self.user.key().id():
                return self.render("error_page.html",
                                   error="You are not the owner" +
                                   "of this comment")

            return self.render("edit_comment.html", user=self.user,
                               comment=comment)
        else:
            return self.render("error_page.html",
                               error="Comment does not exists")

    def post(self, comment_id):
        """
        POST method for /blog/comment/edit/<comment_id> action.
        Validates the inputs and redirects the user to the post page
        if validations are ok.
        If not, render the edit comment's page, keeping the field values,
        and show error messages.
        """

        if not self.user:
            return self.redirect("/login")

        input_comment = self.request.get("comment")
        comment = Comment.by_id(int(comment_id))

        if not input_comment:
            comment_error = True
            return self.render("edit_comment.html", user=self.user,
                               comment=comment, comment_error=comment_error)
        comment.comment = input_comment
        comment.put()

        time.sleep(0.5)

        return self.redirect("/blog/post/%s" % comment.post.key().id())


class BlogDeleteComment(Handler):
    """
    Handler for the delete comment in posts action.
    """
    def post(self, comment_id):
        """
        POST method for /blog/comment/delete/<comment_id> action.
        Validates the current user and if they can delete the post and remove
        the comment from the database.
        """

        if not self.user:
            return self.redirect("/login")

        comment = Comment.by_id(int(comment_id))

        if comment.user.key().id() == self.user.key().id():
            comment.delete()

            time.sleep(0.5)

            return self.redirect("/blog/post/%s" % comment.post.key().id())
        else:
            return self.redirect("/blog/post/%s" % comment.post.key().id(),
                                 error=True)


class BlogError(Handler):
    """
    Handler for the errors in general for the application.
    """
    def get(self, error=""):
        """
        GET method for /error action.
        Render an error page with a default or personalized error message.
        """
        if not error:
            return self.render("error_page.html",
                               error="Something wrong happened or an invalid" +
                               "action was dispatched.")

        self.render("error_page.html", error=error)


app = webapp2.WSGIApplication([
    ("/", BlogMain),
    ("/signup", SignupHandler),
    ("/welcome", WelcomeHandler),
    ("/login", LoginHandler),
    ("/logout", LogoutHandler),
    ("/blog/posts", BlogMainPosts),
    ("/blog/post/new", BlogNewPost),
    ("/blog/post/([0-9]+)", BlogShowPost),
    ("/blog/post/edit/([0-9]+)", BlogEditPost),
    ("/blog/post/delete/([0-9]+)", BlogDeletePost),
    ("/blog/post/like/([0-9]+)", BlogLikePost),
    ("/blog/comment/edit/([0-9]+)", BlogEditComment),
    ("/blog/comment/delete/([0-9]+)", BlogDeleteComment),
    ("/error", BlogError)
], debug=True)


def handle_404(request, response, exception):
    """
    Handle 404 responses for the requests in the blog.
    """
    logging.exception(exception)
    blog_error = BlogError(request, response)
    return blog_error.get("Page not found")


app.error_handlers[404] = handle_404
