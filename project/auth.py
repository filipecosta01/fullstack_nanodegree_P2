"""
.
"""
import re

SECRET = "h1kLLopo"

USERNAME_REGULAR_EXPRESSION = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_REGULAR_EXPRESSION = re.compile(r"^.{3,20}$")
EMAIL_REGULAR_EXPRESSION = re.compile(r"^[\S]+@[\S]+.[\S]+$")


def verify_username(username):
    return USERNAME_REGULAR_EXPRESSION.match(username)

def verify_password(password):
    return password and re.compile(PASSWORD_REGULAR_EXPRESSION).match(password)

def verify_email(email):
    return not email or re.compile(EMAIL_REGULAR_EXPRESSION).match(email)

def verify_match(password, verify):
    return password == verify

