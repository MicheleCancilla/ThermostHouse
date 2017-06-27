#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    File that allows:
     - registration of a new user
     - send of confirmation email
     - confirm of the email
"""

from framework.request_handler import ThermostHouseRequestHandler
from models.users import Users
from google.appengine.api import mail
from conf.configuration_reader import conf, secret

import re
import logging


class RegisterUser(ThermostHouseRequestHandler):
    def get(self):
        try:
            # No register page if already logged in
            if self.check_user_logged_in:
                return self.redirect('/home')
            else:
                return self.render('register/register.html')
        except Exception as ex:
            error_msg = "Exception '{ex}', {ex_type} "
            logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
            self.render('communication/error.html', mail=conf['EMAIL_RECEIVER'])

    @classmethod
    def send_email(cls, to, user_id, confirmation_code, name):
        # the sender must come from our domain
        # appspotmail for this function!
        email_object = mail.EmailMessage(
            sender=conf['EMAIL_SENDER'],
            subject='Hello ' + name + ' confirm your ThermostHouse account',
            to=to,
        )

        email_parameters = {
            'domain': conf['DOMAIN_GOOGLE'],
            'user_id': user_id,
            'confirmation_code': confirmation_code,
            'name': name,
        }
        html_from_template = cls.jinja_env.get_template('register/confirmation_email.html'). \
            render(email_parameters)
        email_object.html = html_from_template
        email_object.send()

    def post(self):
        try:
            name = self.request.get('name')
            email = self.request.get('email')
            password = self.request.get('password')
            status = 200

            # All parameters must be true
            if name and email and password:
                name = name.title()

                if len(name) > 15:
                    status = 400
                    json_response = {
                        'created': False,
                        'title': 'Username troppo lungo',
                        'message': 'La lunghezza massima è di 15 caratteri'
                    }
                else:

                    email_validation_pattern = conf['EMAIL_VALIDATION_PATTERN']

                    if re.match(email_validation_pattern, email):
                        # Mail has a valid structure
                        user = Users.add_new_user(name, email, password)

                        if user['created']:

                            html = self.jinja_env.get_template('register/register_success.html').render()
                            json_response = {
                                'html': html
                            }
                            self.send_email(to=email, user_id=user['user_id'],
                                            confirmation_code=user['confirmation_code'],
                                            name=name)
                            self.send_cookie(name='User', value=user['user_id'])

                        else:
                            status = 400
                            json_response = user
                    else:
                        status = 400
                        json_response = {
                            'created': False,
                            'title': 'La mail non è valida',
                            'message': 'Inserire un indirizzo email valido per poter continuare'
                        }

            else:
                # failure
                status = 400
                json_response = {}

                if not name:
                    json_response.update({
                        'title': 'Il campo username è necessario',
                        'message': 'Inserisci il tuo username per poter continuare'
                    })
                elif not email:
                    json_response.update({
                        'title': 'Il campo email è necessario',
                        'message': 'Inserisci una mail valida per poter continuare'
                    })

                elif not password:
                    json_response.update({
                        'title': 'Il campo password è necessario',
                        'message': 'Inserisci la password per poter continuare'
                    })

            self.json_response(status_code=status, **json_response)

        except Exception as ex:
            error_msg = "Exception '{ex}', {ex_type} "
            logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
            self.render('communication/error.html', mail=conf['EMAIL_RECEIVER'])


class ConfirmUser(ThermostHouseRequestHandler):
    """
        Handler for confirmation of internal user
    """

    def get(self, user_id, confirmation_code):
        try:
            confirmed = False
            user = Users.get_by_id(int(user_id))

            if user:
                if user.confirmation_code == confirmation_code:
                    user.confirmed_email = True
                    user.put()
                    confirmed = user.confirmed_email

            tpl_values = {
                'email_confirmed': confirmed
            }
            print "ciao"
            self.render('register/mail_confirmation_page.html', **tpl_values)

        except Exception as ex:
            error_msg = "Exception '{ex}', {ex_type} "
            logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
            self.render('communication/error.html', mail=conf['EMAIL_RECEIVER'])


class ConfirmRegistration(ThermostHouseRequestHandler):
    def get(self):
        self.render("register/register_success.html")
