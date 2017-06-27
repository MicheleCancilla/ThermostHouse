#!/usr/bin/env python
# -*- coding:utf-8 -*-

from conf.configuration_reader import conf
from framework.request_handler import ThermostHouseRequestHandler
import logging

from os import urandom
import base64


class UserAccount(ThermostHouseRequestHandler):
    """
    Class that shows the user's thermostats
    """
    def set_usr_data(self, authenticated_user):
        if authenticated_user is None:
            return None

        usr_data = {}

        usr_data.update({'username': authenticated_user.username})

        if authenticated_user.image and not authenticated_user.google:
            encoded_image = base64.b64encode(authenticated_user.image)
            src = "data:image/gif;base64," + encoded_image
            usr_data.update({'image': src})
        else:
            usr_data.update({'image': authenticated_user.image})

        usr_data.update({'email': authenticated_user.email})

        usr_data.update({'urlsafeKey': authenticated_user.key.urlsafe()})

        if authenticated_user.API_Key is not None:
            usr_data.update({'API_Key': authenticated_user.API_Key})
        else:
            usr_data.update({'API_Key': None})

        return usr_data

    @ThermostHouseRequestHandler.login_required  # restrict access for not logged users
    def get(self):
        # get the user information
        user = self.check_user_logged_in
        try:
            user_data = self.set_usr_data(user)
            tpl_values = {
                'user_data': user_data,
            }
            # Carico la pagina con i parametri degli utenti
            return self.render('account/user_profile.html', **tpl_values)
        except Exception as ex:
            error_msg = "Exception '{ex}', {ex_type} "
            logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
            return self.render('communication/error.html', mail=conf['EMAIL_RECEIVER'])


class Api(ThermostHouseRequestHandler):
    """
    Generates the user's token API
    """
    @ThermostHouseRequestHandler.login_required
    def get(self):
        user = self.check_user_logged_in
        key = base64.b64encode(urandom(40)).decode('utf-8')

        try:
            user.API_Key = key
            user.put()
        except Exception as ex:
            error_msg = "Exception '{ex}', {ex_type} "
            logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
            return self.render('communication/error.html', mail=conf['EMAIL_RECEIVER'])
        return self.redirect("/account")
