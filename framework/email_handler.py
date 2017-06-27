#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    This file handles the sending email request
"""

import jinja2
import os
from google.appengine.api import mail

from conf.configuration_reader import conf

template_directory = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), 'templates')

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_directory),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)


def send_email(to, user_id, confirmation_code, name):
    # Sender must come from appspotmail domain
    email_object = mail.EmailMessage(
        sender=conf['EMAIL_SENDER'],
        subject='Ciao ' + name + ' conferma il tuo account ThermostHouse',
        to=to,
    )

    email_parameters = {
        'domain': conf['DOMAIN_GOOGLE'],
        'user_id': user_id,
        'confirmation_code': confirmation_code,
        'name': name,
    }

    html_from_template = jinja_env.get_template('register/confirmation_email.html').render(email_parameters)
    email_object.html = html_from_template
    email_object.send()


def send_welcome_email(to, user_id, confirmation_code, name):
    # Sender must come from appspotmail domain
    email_object = mail.EmailMessage(
        sender=conf['EMAIL_SENDER'],
        subject='Ciao ' + name + ' il tuo account ThermostHouse è stato creato',
        to=to,
    )

    email_parameters = {
        'domain': conf['DOMAIN_GOOGLE'],
        'user_id': user_id,
        'confirmation_code': confirmation_code,
        'name': name,
    }

    html_from_template = jinja_env.get_template('email/welcome_email.html').render(
        email_parameters)
    email_object.html = html_from_template
    email_object.send()
