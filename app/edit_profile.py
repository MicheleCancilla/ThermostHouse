#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    File for the user profile customization:
      - change of password;
      - change personal information;
"""

from framework.request_handler import ThermostHouseRequestHandler
from conf.configuration_reader import conf
from google.appengine.api import images
import logging
from base64 import b64encode
from hashlib import sha256

from os import urandom


class EditProfile(ThermostHouseRequestHandler):
    """
        Handler for edit user profile
    """

    @ThermostHouseRequestHandler.login_required
    def get(self):

        usr = self.check_user_logged_in
        usr_image = None

        if usr.image:
            encoded_image = b64encode(usr.image)
            usr_image = "data:image/gif;base64," + encoded_image

        self.render('account/edit_profile.html', usr_image=usr_image)

    @ThermostHouseRequestHandler.login_required
    def post(self):
        user = self.check_user_logged_in

        # change the name
        if self.request.get('username') and self.request.get('username') != user.username:
            user.username = self.request.get('username')

        if self.request.get('fileUser'):
            image = self.request.get('fileUser')
            # user.image = image
            user.image = images.resize(image, 160, 160)
        elif user.image:
            user.image = user.image

        try:
            user.put()
            # redirect to user page
            self.redirect('/account')
        except Exception as ex:
            error_msg = "Exception '{ex}', {ex_type} "
            logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
            self.render('communication/error.html', mail=conf['EMAIL_RECEIVER'])


class ChangePassword(ThermostHouseRequestHandler):
    """
        Handler for changing the password

    """

    @ThermostHouseRequestHandler.login_required
    def get(self):
        self.render("account/change_password.html")

    @ThermostHouseRequestHandler.login_required
    def post(self):
        try:
            password = self.request.get("password")
            user = self.check_user_logged_in
            if user:
                random_bytes = urandom(64)
                salt = b64encode(random_bytes).decode('utf-8')
                hashed_password = salt + sha256(salt + password).hexdigest()
                user.password = hashed_password
                user.put()
                tpl_values = {
                    'user_password_changed': True
                }
                return self.render("account/change_password.html", **tpl_values)

            return self.redirect('/edit_profile')

        except Exception as ex:
            error_msg = "Exception '{ex}', {ex_type} "
            logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
            self.render('communication/error.html', mail=conf['EMAIL_RECEIVER'])
