#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    Il file login_manager.py serve per gestire tutti i tipi di login (Facebook e  Google) e di logout degli utenti

"""
import logging
import urllib2

from google.appengine.api import users
from oauth2client import client

from app.decorator import decorator, service
from conf.configuration_reader import conf
from framework.request_handler import ThermostHouseRequestHandler
from models.users import Users


class GoogleLogin(ThermostHouseRequestHandler):
    """
    Login with Google: use the decorator object for oauth2 authentication
    """

    @decorator.oauth_aware
    def get(self):
        if decorator.has_credentials():
            try:
                # user = service.people().get(resourceName='people/me').execute(decorator.http())
                user = service.people().get(userId='me').execute(http=decorator.http())
                # an user has a structure like

                # {u'url': u'https://plus.google.com/100334024248793840757',
                #  u'etag': u'"FT7X6cYw9BSnPtIywEFNNGVVdio/B_3uJwqF3_rX3O_OxyOjcpy3l_M"',
                #  u'image': {
                #      u'url': u'https://lh3.googleusercontent.com/XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg?sz=50',
                #      u'isDefault': True},
                #  u'emails': [{u'type': u'account', u'value': u'pritttt4@gmail.com'}],
                #  u'ageRange': {u'max': 20, u'min': 18},
                #  u'kind': u'plus#person',
                #  u'id': u'100334024248793840757',
                #  u'isPlusUser': True,
                #  u'objectType': u'person',
                #  u'verified': False,
                #  u'circledByCount': 0,
                #  u'name': {u'familyName': u'Cancilla', u'givenName': u'Michele'}, u'displayName': u'Michele Cancilla',
                #  u'language': u'it'}

                name = user['displayName']
                email = user['emails'][0]['value']
                image_url = str(user['image']['url'])
                id = str(user['id'])

                # cut the "?sz=50" at the end
                image_url, none = image_url.split('?')

                our_user = Users.check_if_exists(email)
                if not our_user:
                    dict = Users.add_new_user(name, email, '123password321', False, True, False, None, id)
                    Users.add_image(image_url, dict['user_id'])
                    Users.automatic_confirm_email(dict['user_id'])
                    try:
                        if email:
                            self.send_welcome_email(to=email, user_id=dict['user_id'],
                                                    confirmation_code=dict['confirmation_code'],
                                                    name=name)
                    except Exception as ex:
                        error_msg = "Exception: problems with email, {ex_type} "
                        logging.error(error_msg.format(ex_type=type(ex)))
                    self.send_cookie(name='User', value=dict['user_id'])
                else:
                    self.send_cookie(name='User', value=our_user.key.id())
            except client.AccessTokenRefreshError as ex:
                error_msg = "Exception: Access Token Refresh Error, retry to login, {ex_type}"
                logging.error(error_msg.format(ex_type=type(ex)))
                self.redirect('/home')
            return self.redirect('/home')
        else:
            url = decorator.authorize_url()

            # redirect to google authorize page
            return self.redirect(url)


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

            our_user = Users.check_if_exists(email)
            if not our_user:
                # Genero una password casuale per poter creare l'utente (in futuro l'utente potrà accedere al
                # servizio usando il login intero, per farlo dovrà semplicemente modificare la password)
                dict = Users.add_new_user(name, email, '123password321', True, False, False, id)
                Users.add_image(html_image, dict['user_id'])
                Users.automatic_confirm_email(dict['user_id'])
                try:
                    if email:
                        self.send_welcome_email(to=email, user_id=dict['user_id'],
                                                confirmation_code=dict['confirmation_code'],
                                                name=name)
                except Exception as ex:
                    error_msg = "Exception: problems with email, {ex_type} "
                    logging.error(error_msg.format(ex_type=type(ex)))

                self.send_cookie(name='User', value=dict['user_id'])
            else:
                self.send_cookie(name='User', value=our_user.key.id())
            return self.redirect('/home')

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
            return self.redirect('/')

        except Exception as ex:
            error_msg = "Exception '{ex}', {ex_type} "
            logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
            self.render('communication/error.html', mail=conf['EMAIL_RECEIVER'])
