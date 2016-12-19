#!/usr/bin/env python
# -*- coding:utf-8 -*-

from google.appengine.ext import ndb
from hashlib import sha256
from base64 import b64encode
from os import urandom
from models.address import Address
import uuid


class Users(ndb.Model):
    username = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)

    confirmation_code = ndb.StringProperty(required=True)
    confirmed_email = ndb.BooleanProperty(default=False)

    timestamp = ndb.DateTimeProperty(auto_now_add=True)  # Date della registrazione

    facebookID = ndb.IntegerProperty()  # Id di Facebook
    googleID = ndb.StringProperty()  # Id di Google
    twitterID = ndb.StringProperty()  # Id di Twitter

    facebook = ndb.BooleanProperty(default=False)  # Vera se è un utente di Facebook
    google = ndb.BooleanProperty(default=False)  # Vera se è un utente di Google
    twitter = ndb.BooleanProperty(default=False)  # Vera se è un utente di Twitter

    image = ndb.BlobProperty()  # Avatar dell'utente

    address = ndb.StructuredProperty(Address)

    @classmethod
    def check_if_exists(cls, email):
        return cls.query(cls.email == email).get()

    @classmethod
    def add_new_user(cls, username, email, password, facebook=False, google=False, twitter=False, face_id=None):
        user = cls.check_if_exists(email)

        if not user:
            if len(password) < 5:
                return {
                    'created': False,
                    'title': 'Password troppo breve',
                    'message': 'La password deve contenere almeno 5 caratteri'
                }
            else:
                # Creazione del sale: generato casualmente e diverso per tutti gli utenti
                random_bytes = urandom(64)
                salt = b64encode(random_bytes).decode('utf-8')

                # sha256 restituisce un oggetto che converto in stringa con hexdigest
                hashed_password = salt + sha256(salt + password).hexdigest()

                # Il sale e la password possono essere salvati nello stesso campo perche il sale ha lunghezza fissa

                # Il confirmation code per il check dell'email viene generato random
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
                ).put()

                return {
                    'created': True,
                    'user_id': new_user_key.id(),
                    'confirmation_code': confirmation_code,
                }

        else:
            # Mail gia presente
            return {
                'created': False,
                'title': 'La mail è già in uso',
                'message': 'Esegui il login se hai gi\a'' un account'
            }

    @classmethod
    def add_image(cls, image, user_id):
        # La funzione di ricerca per chiavi vuole in ingresso una lista di chiavi
        usr = Users.get_by_id(int(user_id))
        if usr and image is not None:
            usr.image = image
            usr.put()

    """ Return the ID of the user if exists"""
    @classmethod
    def check_password(cls, email, password):
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
        # Un utente che si registra con un sistema di autenticazione esterno non ha bisogno di confermare la mail
        usr = Users.get_by_id(usr_id)
        if usr:
            usr.confirmed_email = True
            usr.put()

    @classmethod
    def get_users(cls):
        qry = cls.query()
        return qry