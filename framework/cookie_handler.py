#!/usr/bin/env python
# -*- coding:utf-8 -*-

from hashlib import sha256

# obtained with 'b64encode(urandom(64)).decode('utf-8')' command
SECRET = "2MFgycfohI/F7cfzbiQ46Cm9TLY8J2PGMChJuYJMNtOPUMjMmhurJukWC1jZxKQa/cPXadkwXbjva9Mn20ZQNw=="


def sign_cookie(value):  # pass teh value to sign
    string_value = str(value)
    signature = sha256(SECRET + string_value).hexdigest()
    return signature + "|" + string_value


def check_cookie(value):  # accept a parameter formatted as [signature|value]
    signature = value[:value.find('|')]  # slice from 0 to '|'
    declared_value = value[value.find('|') + 1:]  # slice from '|'+1 to end

    if sha256(SECRET + declared_value).hexdigest() == signature:
        return declared_value
    else:
        return None
