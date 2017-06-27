#!/usr/bin/env python
# -*- coding:utf-8 -*-

import uuid
import os
from base64 import b64encode
from hashlib import sha256
from os import urandom

from google.appengine.ext import ndb

from models.thermostats import Thermostats
from google.appengine.api import images


class Users(ndb.Model):
    username = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)

    confirmation_code = ndb.StringProperty(required=True)
    confirmed_email = ndb.BooleanProperty(default=False)

    # Date of registration
    timestamp = ndb.DateTimeProperty(auto_now_add=True)

    facebookID = ndb.IntegerProperty()  # Facebook Id
    googleID = ndb.StringProperty()  # Google Id
    twitterID = ndb.StringProperty()  # Twitter Id

    facebook = ndb.BooleanProperty(default=False)
    google = ndb.BooleanProperty(default=False)
    twitter = ndb.BooleanProperty(default=False)

    image = ndb.BlobProperty()  # Avatar dell'utente

    # An user can have more than one thermostat
    # thermostat = ndb.KeyProperty(kind='Thermostats', repeated=True)

    API_Key = ndb.StringProperty(default=None)

    @classmethod
    def check_if_exists(cls, email):
        return cls.query(cls.email == email).get()

    @classmethod
    def add_new_user(cls, username, email, password, facebook=False, google=False, twitter=False, face_id=None,
                     google_id=None):
        user = cls.check_if_exists(email)

        if not user:
            if len(password) < 5:
                return {
                    'created': False,
                    'title': 'Password troppo breve',
                    'message': 'La password deve contenere almeno 5 caratteri'
                }
            else:
                # Salt creation, generated randomly and different for each user
                random_bytes = urandom(64)
                salt = b64encode(random_bytes).decode('utf-8')

                hashed_password = salt + sha256(salt + password).hexdigest()

                # Il sale e la password possono essere salvati nello stesso campo perche il sale ha lunghezza fissa

                # Random confirmation code
                confirmation_code = str(uuid.uuid4().get_hex())

                new_user_key = cls(
                    username=username,
                    email=email,
                    password=hashed_password,
                    confirmation_code=confirmation_code,
                    google=google,
                    facebook=facebook,
                    twitter=twitter,
                    facebookID=face_id,
                    googleID=google_id,
                ).put()

                return {
                    'created': True,
                    'user_id': new_user_key.id(),
                    'confirmation_code': confirmation_code,
                }

        else:
            # Mail already exists
            return {
                'created': False,
                'title': 'La mail è già in uso',
                'message': 'Esegui il login se hai gi\a'' un account'
            }

    @classmethod
    def add_image(cls, image, user_id):
        # get the user by user_id
        user = Users.get_by_id(int(user_id))
        if user and image is not None:
            user.image = image
            user.put()

    @classmethod
    def check_password(cls, email, password):
        """ Return the ID of the user if exists"""
        user = cls.check_if_exists(email)

        if user:
            # user exists
            hashed_password = user.password
            salt = hashed_password[0:88]  # slice the string and extracts 0-88 characters

            check_password = salt + sha256(salt + password).hexdigest()
            if check_password == hashed_password:
                return user.key.id()  # returns the id of the user
            else:
                return None  # the password doesn't match
        else:
            return None

    @classmethod
    def automatic_confirm_email(cls, usr_id):
        # Confirmed automatically if external authentication method is used
        usr = Users.get_by_id(usr_id)
        if usr:
            usr.confirmed_email = True
            usr.put()

    @classmethod
    def get_users(cls):
        qry = cls.query()
        return qry

    @classmethod
    def get_usr_by_key(cls, key):
        if not key:
            return None
        else:
            return ndb.gql("SELECT * FROM Users where __key__ IN :1", key)

    @classmethod
    def get_owned_thermostats(cls, user):
        """Returns all the thermostats owned by AN user"""
        return Thermostats.get_thermostats_by_owner(user.key)

