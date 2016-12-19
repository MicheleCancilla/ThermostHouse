#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    email_handler.py è il file per la gestione dell'invio di mail

"""

from google.appengine.api import mail
from conf.configuration_reader import conf
import os
import jinja2

# ###################################################################### #
# Template: configurazione iniziale JINJA2                               #
# ###################################################################### #

template_directory = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), 'templates')

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_directory),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)


def send_email(to, user_id, confirmation_code, name):
    # Il sender deve provenire dal dominio dell'applicazione: appspotmail per questa funzione
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

    # Gli stili sono stati inclusi direttamente nel codice html perchè, per ragioni di sicurezza, la mail non può
    # includere fogli di stile CSS
    html_from_template = jinja_env.get_template('register/confirmation_email.html').render(email_parameters)
    email_object.html = html_from_template
    email_object.send()


def send_welcome_email(to, user_id, confirmation_code, name):
    # Il sender deve provenire dal dominio dell'applicazione: appspotmail per questa funzione
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

    # Gli stili sono stati inclusi direttamente nel codice html perchè, per ragioni di sicurezza, la mail non può
    # includere fogli di stile CSS
    html_from_template = jinja_env.get_template('email/welcome_email.html').render(
        email_parameters)
    email_object.html = html_from_template
    email_object.send()
