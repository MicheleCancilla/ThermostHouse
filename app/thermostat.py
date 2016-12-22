#!/usr/bin/env python
# -*- coding:utf-8 -*-

from framework.request_handler import ThermostHouseRequestHandler
from conf.configuration_reader import conf
from google.appengine.api import search
from google.appengine.ext import ndb
from models.users import Users
from models.address import Address
from models.thermostats import Thermostats
import base64
import copy
import logging


class ThermostatPage(ThermostHouseRequestHandler):
    def set_auth_thermostat_data(self, auth_thermostat_user):
        if auth_thermostat_user is None or auth_thermostat_user.thermostat is None:
            return None

        thermostat_data = {}

        thermostat_data.update({'user': auth_thermostat_user.thermostat.user})
        thermostat_data.update({'name': auth_thermostat_user.thermostat.name})
        thermostat_data.update({'house': auth_thermostat_user.thermostat.house})
        thermostat_data.update({'temperature': auth_thermostat_user.thermostat.temperature})
        thermostat_data.update({'hysteresis': auth_thermostat_user.thermostat.hysteresis})
        thermostat_data.update({'urlsafeKey': auth_thermostat_user.key.urlsafe()})

        return thermostat_data

    def set_thermostat_data(self, qry, auth_thermostat_user_key):
        if qry is None:
            return None

        # Preparo i valori caricandoli in un dizionario (ad ogni giro devo azzerare il dizionario)
        list = []
        thermostat_data = {}
        for data in qry:
            if data.key == auth_thermostat_user_key or not data.thermostat:
                # Casi "particolari" che non devono essere gestiti in questa situazione:
                # - L'impianto è  dell'utente autenticato;
                # - L'utente corrente non dispone di un impianto
                pass
            else:
                # Vuoto il dizionario per il giro successivo
                thermostat_data.clear()

                thermostat_data.update({'user': data.thermostat.user})
                thermostat_data.update({'name': data.thermostat.name})
                thermostat_data.update({'home': data.thermostat.home})
                thermostat_data.update({'temperature': data.thermostat.temperature})
                thermostat_data.update({'hysteresis': data.thermostat.hysteresis})
                thermostat_data.update({'urlsafeKey': data.key.urlsafe()})

                # Aggiungo l'elemento corrente alla lista
                list.append(copy.deepcopy(thermostat_data))

        return list

    @ThermostHouseRequestHandler.login_required
    def get(self):

        """ Visualizza le informazioni dei termostati, se già aggiunti. Altrimenti permette di
        aggiungerne uno
        """
        user = self.request.get('user')

        # Utente autenticato
        auth_thermostat_user, auth_thermostat_user_key = self.get_auth_user()
        list = []

        if user == "":
            # Devo visualizzare tutti termostati

            qry = Users.get_user_thermostats()
            print qry
            list = self.set_thermostat_data(qry, auth_thermostat_user_key)  # Carico correttamente i valori nella list
        else:
            # E' stato specificato un utente tramite URL, eseguo la ricerca
            reconstructed_key = ndb.Key(urlsafe=user)

            if reconstructed_key != auth_thermostat_user_key:
                # Eseguo la ricerca
                qry = ndb.gql('SELECT * FROM Users where __key__ IN :1', [reconstructed_key])
                list = self.set_thermostat_data(qry,
                                                auth_thermostat_user_key)  # Carico correttamente i valori nella list
                auth_thermostat_user = None

        # Carico la pagina con i parametri degli utenti
        self.render('thermostat-page/thermostat-page.html',
                    auth_thermostat=self.set_auth_thermostat_data(auth_thermostat_user),
                    thermostat_data=list)
        # def get(self):
        #     """ Visualizza le informazioni dei termostati, se già aggiunti. Altrimenti permette di
        #     aggiungerne uno
        #     """
        #     user = self.request.get('user')
        #
        #     # Utente autenticato
        #     auth_thermostat_user, auth_thermostat_user_key = self.get_auth_user()
        #     list = []
        #
        #     if user == "":
        #         # Devo visualizzare tutti termostati
        #
        #         qry = Users.get_user_thermostats()
        #         list = self.set_thermostat_data(qry, auth_thermostat_user_key)  # Carico correttamente i valori nella list
        #     else:
        #         # E' stato specificato un utente tramite URL, eseguo la ricerca
        #         reconstructed_key = ndb.Key(urlsafe=user)
        #
        #         if reconstructed_key != auth_thermostat_user_key:
        #             # Eseguo la ricerca
        #             qry = ndb.gql('SELECT * FROM Users where __key__ IN :1', [reconstructed_key])
        #             list = self.set_thermostat_data(qry,
        #                                             auth_thermostat_user_key)  # Carico correttamente i valori nella list
        #             auth_thermostat_user = None
        #
        #     # Carico la pagina con i parametri degli utenti
        #     self.render('thermostat-page/thermostat-page.html',
        #                 auth_thermostat=self.set_auth_thermostat_data(auth_thermostat_user),
        #                 thermostat_data=list)


class CreateThermostat(ThermostHouseRequestHandler):
    @ThermostHouseRequestHandler.login_required
    def get(self):
        self.render("thermostat-page/create-thermostat.html")

    @ThermostHouseRequestHandler.login_required
    def post(self):
        user = self.check_user_logged_in

        # Acquisizione dei dati dell'indirizzo
        address = Address()
        address.province = self.request.get('province')
        try:
            address.zip_code = int(self.request.get('zip_code'))
            address.number = int(self.request.get('number'))
        except ValueError:
            # L'eventualità che il parametro inserito non sia un numero è gestita lato client dal browser
            pass

        address.region = self.request.get('region')
        address.street = self.request.get('street')
        address.city = self.request.get('city')

        # Chiamo la funzione di Geolocalizzazione su indirizzo
        status_geocode = address.geocode()

        if status_geocode == 0:
            # La localizzazione è andata a buon fine, proseguo

            # Acquisizione dei dati del termostato
            therm = Thermostats()
            try:
                therm.user = user.key
                therm.name = self.request.get('nameTH')
                therm.house = address
                therm.put()
                user.thermostat = therm
                user.put()
                self.redirect('/thermostat')
            except Exception as ex:
                error_msg = "Exception '{ex}', {ex_type} "
                logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
                self.render('communication/error.html', mail=conf['EMAIL_RECEIVER'])

        else:
            # La localizzazione non è riuscita, mostro un messaggio di errore
            self.render("communication/bad_location.html")
