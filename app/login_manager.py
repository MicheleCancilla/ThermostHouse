#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    Il file login_manager.py serve per gestire tutti i tipi di login (Facebook e  Google) e di logout degli utenti

"""
from conf.configuration_reader import conf, secret
from framework.request_handler import ThermostHouseRequestHandler
from google.appengine.api import users
from google.appengine.api import memcache
from apiclient.discovery import build
from oauth2client.appengine import OAuth2Decorator  # oauth2Client è incluso in google-api-python-client

import logging
import urllib2
import httplib2
import logging


# decoratorPlus = OAuth2Decorator(
#     client_id=secret['CLIENT_ID'],
#     client_secret=secret['CLIENT_SECRET'],
#     scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/calendar',
#     approval_prompt='force')
#
# try:
#     service = build("plus", "v1")
# except Exception as ex:
#     error_msg = "Exception '{ex}', {ex_type} "
#     logging.error(error_msg.format(ex=ex, ex_type=type(ex)))

class GoogleLogin(ThermostHouseRequestHandler):
    """
        Per la gestione del login con Google: la classe fa uso dell'istanza user offerta da Google

    """

    # @decoratorPlus.oauth_required
    def get(self):
        try:

            # Acquisisco l'utente di google corrente
            user = users.get_current_user()
            # Se l'utente è effettivamente un utente di google e ha le credenziali


            if user:
                # Se non esiste nel nostro database lo inseriamo
                from models.users import Users as InternalUser

                our_user = InternalUser.check_if_exists(user.email())

                if not our_user:
                    name = user.nickname().title()

                    # Genero una password casuale per poter creare l'utente (in futuro l'utente potrà accedere al
                    # servizio usando il login intero, per farlo dovrà semplicemente modificare la password)
                    dict = InternalUser.add_new_user(name, user.email(), '123password321', False, True, False)

                    # html_image = self.get_google_image()

                    InternalUser.automatic_confirm_email(dict['user_id'])
                    # InternalUser.add_image(html_image, dict['user_id'])
                    try:
                        self.send_welcome_email(to=user.email(), user_id=dict['user_id'],
                                                confirmation_code=dict['confirmation_code'], name=name, )

                    except Exception as ex:
                        error_msg = "Exception: problems with email, {ex_type} "
                        logging.error(error_msg.format(ex_type=type(ex)))

                    self.send_cookie(name='User', value=dict['user_id'])

                else:
                    self.send_cookie(name='User', value=our_user.key.id())

                return self.redirect('/')
            else:
                return self.redirect(users.create_login_url(self.request.uri))

        except Exception as ex:
            error_msg = "Exception '{ex}', {ex_type} "
            logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
            self.render('communication/error.html', mail=conf['EMAIL_RECEIVER'])


class FacebookLogin(ThermostHouseRequestHandler):
    """
        Per la gestione del login con Facebook
    """

    def post(self):
        try:
            # Questa funzione fa riferimento agli script java contenuti nei seguenti file html
            #   - templates/login/register_controller.js.html
            #   - templates/login/login_controller.js.html

            name = self.request.get('name')
            email = self.request.get('email')
            id = int(self.request.get('id'))
            html_image = None
            if (self.request.get('image')) != "undefined":
                try:
                    image_url = "http://" + (self.request.get('image'))
                    response = urllib2.urlopen(image_url)
                    html_image = response.read()
                except Exception as ex:
                    html_image = None
                    error_msg = "Exception '{ex}', {ex_type} "
                    logging.error(error_msg.format(ex=ex, ex_type=type(ex)))

            from models.users import Users as InternalUser

            our_user = InternalUser.check_if_exists(email)
            if not our_user:
                # Genero una password casuale per poter creare l'utente (in futuro l'utente potrà accedere al
                # servizio usando il login intero, per farlo dovrà semplicemente modificare la password)
                dict = InternalUser.add_new_user(name, email, '123password321', True, False, False, id)
                InternalUser.add_image(html_image, dict['user_id'])
                InternalUser.automatic_confirm_email(dict['user_id'])
                try:
                    if email:
                        self.send_welcome_email(to=email, user_id=dict['user_id'],
                                                confirmation_code=dict['confirmation_code'],
                                                name=name, )
                except Exception as ex:
                    error_msg = "Exception: problems with email, {ex_type} "
                    logging.error(error_msg.format(ex_type=type(ex)))

                self.send_cookie(name='User', value=dict['user_id'])
            else:
                self.send_cookie(name='User', value=our_user.key.id())
            return self.redirect('/account')

        except Exception as ex:
            error_msg = "Exception '{ex}', {ex_type} "
            logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
            self.render('communication/error.html', mail=conf['EMAIL_RECEIVER'])


class LogOut(ThermostHouseRequestHandler):
    def get(self):
        try:

            # Elimino il cookie primario (faccio il logout)
            self.response.delete_cookie("User")

            # Se è un utente Google faccio il logout da Google
            user = users.get_current_user()
            if user:
                return self.redirect(users.create_logout_url('/'))

            # Altrimenti ridireziono alla home
            return self.redirect('/account')

        except Exception as ex:
            error_msg = "Exception '{ex}', {ex_type} "
            logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
            self.render('communication/error.html', mail=conf['EMAIL_RECEIVER'])
