#!/usr/bin/env python
# -*- coding:utf-8 -*-

from webapp2 import RequestHandler, cached_property
import os
import jinja2


class ThermostHouseRequestHandler(RequestHandler):
    templates_dir = os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)),
        'templates')

    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates_dir)
    )

    def render(self, template, **kwargs):
        #aggiungo l'user nella risposta se questo è loggato
        user = self.check_user_logged_in
        kwargs.update({
            'user': user,
        })
        jinja_template = self.jinja_env.get_template(template)
        html_from_template = jinja_template.render(kwargs)
        self.response.out.write(html_from_template)

    def render_json(self, template, json, **kwargs):

        # Metodo per il render di template, dati eventuali parametri come dizionario **kwargs e parametri json

        # Se un utente è autenticato invio i parametri per la personalizzazione della pagina
        user = self.check_user_logged_in
        kwargs.update({
            'user': user,
        })
        jinja_template = self.jinja_env.get_template(template)
        html_from_template = jinja_template.render(kwargs, js_data=json)
        self.response.out.write(html_from_template)

    def json_response(self, status_code=200, **kwargs):
        from json import dumps

        self.response.status = status_code
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(dumps(kwargs))

    def read_cookie(self, name):
        from framework.cookie_handler import check_cookie

        cookie_value = self.request.cookies.get(name)
        return check_cookie(cookie_value)

    def send_cookie(self, name, value):
        from framework.cookie_handler import sign_cookie

        signed_cookie_value = sign_cookie(value)
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, signed_cookie_value))

    # Per la gestione delle email in fase di login tramite sistemi di terze parti
    def send_welcome_email(self, to, user_id, confirmation_code, name):
        from framework.email_handler import send_welcome_email
        return send_welcome_email(to, user_id, confirmation_code, name)

    # essentially is a wrapper, remember the output of the function
    @cached_property
    def check_user_logged_in(self):
        """Return an istance of user model"""
        if self.request.cookies.get('User'):
            user_id = self.read_cookie('User')
            if user_id:
                from models.users import Users

                return Users.get_by_id(int(user_id))
            else:
                # user doesn't logged in
                return None
        else:
            # can't identify cookie
            return None

    @staticmethod
    def login_required(handler):  # take a handler (login.post)
        def check_login(self, *args, **kwargs):  # accept all kind of parameters
            if self.check_user_logged_in:
                return handler(self, *args, **kwargs)
            else:
                return self.redirect('/home')

        return check_login

    def get_auth_user(self):
        # Controllo se c'è un utente autenticato
        auth_user = self.check_user_logged_in
        if auth_user:
            auth_user_key = auth_user.key
        else:
            # Non c'è un utente autenticato
            return None, None

        return auth_user, auth_user_key
