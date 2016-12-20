#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    File per la gestione della personalizzazione del profilo utente:
      - cambio della password;
      - cambio delle informazioni personali;
      - cambio dell'indirizzo associato al profilo;
      - cambio delle informazioni riguardanti l'impianto di produzione;

"""

from framework.request_handler import ThermostHouseRequestHandler
from conf.configuration_reader import conf
from models.address import Address
from google.appengine.api import images
import logging
from base64 import b64encode
from hashlib import sha256
import base64
import json

from os import urandom


class EditProfile(ThermostHouseRequestHandler):
    """
        Handler per la gestione della modifica delle informazioni del profilo utente
    """

    @ThermostHouseRequestHandler.login_required
    def get(self):
        # I dati dell'utente per il preload del form vengono utilizzati anche all'interno di script javascript, per
        # tale motivo è necessario gestirli (anche) in formato json
        usr = self.check_user_logged_in
        usr_image = None
        plant_image = None

        if usr.image:
            encoded_image = base64.b64encode(usr.image)
            usr_image = "data:image/gif;base64," + encoded_image

        # if usr.impianto:
        #     if usr.impianto.immagine:
        #         encoded_image = base64.b64encode(usr.impianto.immagine)
        #         plant_image = "data:image/gif;base64," + encoded_image

        supp_dict = {}
        if usr.address:
            supp_dict = {"province": usr.address.province, "region": usr.address.region}
        # if usr.impianto:
        #     supp_dict.update({"tipo": usr.impianto.tipo})
        #     supp_dict.update({"alimentazione": usr.impianto.alimentazione})
        #     supp_dict.update({"noleggio": usr.impianto.noleggio})
        #     supp_dict.update({"descrizione": usr.impianto.descrizione})

        js_data = json.dumps(supp_dict)

        # TODO create change_profile.html
        self.render_json('account/edit_profile.html', js_data, usr_image=usr_image, plant_image=plant_image)

    @ThermostHouseRequestHandler.login_required
    def post(self):
        user = self.check_user_logged_in

        # Acquisizione dei dati dell'utente
        user.username = self.request.get('username')

        if self.request.get('fileUser'):
            image = self.request.get('fileUser')
            user.image = images.resize(image, 200, 200)
        elif user.image:
            user.image = user.image

        # Acquisizione dei dati dell'indirizzo
        ind = Address()
        ind.province = self.request.get('province')
        try:
            ind.zip_code = int(self.request.get('zip_code'))
            ind.number = int(self.request.get('number'))
        except ValueError:
            # L'eventualità che il parametro inserito non sia un numero è gestita lato client dal browser
            pass

        ind.region = self.request.get('region')
        ind.street = self.request.get('street')
        ind.city = self.request.get('city')

        # Chiamo la funzione di Geolocalizzazione su indirizzo
        status_geocode = ind.geocode()

        if status_geocode == 0:
            # La localizzazione è andata a buon fine, proseguo

            # Acquisizione dei dati dell'impianto
            # imp = Impianto()
            # imp.alimentazione = self.request.get('alimtype')
            # try:
            #     imp.capacita = int(self.request.get('capacita'))
            # except ValueError:
            #     # L'eventualità che il parametro inserito non sia un numero è gestita lato client dal browser
            #     pass
            #
            # imp.tipo = self.request.get('tipo')
            # imp.descrizione = self.request.get('descrizione')
            #
            # # Il noleggio è a True di default
            # if self.request.get('nolotype') == 'False':
            #     imp.noleggio = False

            # if self.request.get('file'):
            #     image = self.request.get('file')
            #     imp.immagine = images.resize(image, 200, 200)
            # elif user.impianto:
            #     # Se era disponibile ricarico la vecchia immagine
            #     imp.immagine = user.impianto.immagine

            try:
                user.address = ind
                # user.impianto = imp
                user.put()
                # Al termine della modifica rimando alla pagina dell'utente
                self.redirect('/account?utente=' + user.key.urlsafe())
            except Exception as ex:
                error_msg = "Exception '{ex}', {ex_type} "
                logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
                self.render('communication/error.html', mail=conf['EMAIL_RECEIVER'])
        else:
            # La localizzazione non è riuscita, mostro un messaggio di errore
            self.render("communication/bad_location.html")


class ChangePassword(ThermostHouseRequestHandler):
    """
        Hanler per la gestione della modifica della password

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
                tmp_values = {
                    'user_password_changed': True

                }
                return self.render("account/change_password.html", **tmp_values)

            self.redirect('/edit_profile')

        except Exception as ex:
            error_msg = "Exception '{ex}', {ex_type} "
            logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
            self.render('communication/error.html', mail=conf['EMAIL_RECEIVER'])
