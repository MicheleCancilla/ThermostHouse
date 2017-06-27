#!/usr/bin/env python
# -*- coding:utf-8 -*-

""" File that contains functions useful for cookie"""

from hashlib import sha256

from conf.configuration_reader import secret


def sign_cookie(value):  # pass teh value to sign
    string_value = str(value)
    signature = sha256(secret['COOKIE_SECRET'] + string_value).hexdigest()
    return signature + "|" + string_value


def check_cookie(value):  # accept a parameter formatted as [signature|value]
    signature = value[:value.find('|')]  # slice from 0 to '|'
    declared_value = value[value.find('|') + 1:]  # slice from '|'+1 to end

    if sha256(secret['COOKIE_SECRET'] + declared_value).hexdigest() == signature:
        return declared_value
    else:
        return None
