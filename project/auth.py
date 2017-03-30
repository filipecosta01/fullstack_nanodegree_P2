"""
This module is used for auxiliar methods on authentication flow.
"""
import re

SECRET = "h1kLLopo"

def verify_username(username):
    """
    Verifies the input username is valid according to the regular expression.
    """
    name_reg_exp = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    return username and name_reg_exp.match(username)

def verify_password(password):
    """
    Verifies the input password is valid according to the regular expression.
    """
    password_reg_exp = re.compile(r"^.{3,20}$")
    return password and password_reg_exp.match(password)

def verify_email(email):
    """
    Verifies the input email is valid according to the regular expression.
    """
    email_reg_exp = re.compile(r"^[\S]+@[\S]+.[\S]+$")
    return not email or email_reg_exp.match(email)

def verify_match(password, verify):
    """
    Verifies the password and verify password matches.
    """
    return password == verify

