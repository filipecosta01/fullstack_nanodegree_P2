"""
Utils module to keep functions that does not need objects or any real interaction with them
in the code, so they can be called and used in all of system's modules, just by importing them.
"""
import hashlib
import random
import string
import hmac

SECRET = "kjknjjsjaj"

def make_pw_hash(name, password, salt=None):
    """
    Method that uses hashlib SHA256 algorithm to generate a new hash from name, password and salt,
    passed in parameters.
    The result will be the string with the hash plus pipe '|' plus the salt used in the algorithm.
    """
    if not salt:
        salt = make_salt()
    return "%s,%s" % (hashlib.sha256(name + password + salt).hexdigest(), salt)

def make_salt():
    """
    Method that uses random string letters to generate a salt word, used to create a hash.
    """
    return ''.join(random.choice(string.letters) for i in range(5))

def hash_str(word):
    """
    Return a new hash using hmac library. The hash is formed by the SECRET variable as the seed,
    and the string in the parameter.
    """
    return hmac.new(SECRET, word).hexdigest()

def make_secure_val(word):
    """
    Generate a new hash using the word in the parameter and the hashed value of it.
    """
    return "%s|%s" % (word, hash_str(word))

def check_secure_val(hash):
    """
    Check if a hash value is still valid or if it was tempered somehow.
    """
    value = hash.split("|")[0]
    if hash == make_secure_val(value):
        return value

def check_valid_pw(name, password, hash_value):
    """
    Check if a password is valid by verifying the hash_value in argument and comparing to the
    expected value of it, using salt, name and password in the parameter.
    """
    salt = hash_value.split(',')[1]
    return hash_value == make_pw_hash(name, password, salt)
