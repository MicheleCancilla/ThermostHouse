#!/usr/bin/env python
# -*- coding:utf-8 -*-

import copy
import json
import logging

from google.appengine.ext import ndb

from conf.configuration_reader import conf
from framework.request_handler import ThermostHouseRequestHandler
from models.address import Address
from models.thermostats import Thermostats
from models.users import Users


class ThermostatPage(ThermostHouseRequestHandler):
    @ThermostHouseRequestHandler.login_required
    def set_thermostat_data(self, qry):
        if qry is None:
            return None
        # Preparo i valori caricandoli in un dizionario (ad ogni giro devo azzerare il dizionario)
        list = []
        thermostat_data = {}
        for thermostat in qry:

            if not thermostat:
                # Casi "particolari" che non devono essere gestiti in questa situazione:
                # - L'impianto è  dell'utente autenticato;
                # - L'utente corrente non dispone di un impianto
                pass
            else:
                # Vuoto il dizionario per il giro successivo
                thermostat_data.clear()

                # thermostat_data.update({'user': thermostat.user})
                thermostat_data.update({'name': thermostat.name})
                thermostat_data.update({'house': thermostat.house})
                thermostat_data.update({'temperature': thermostat.temperature})
                thermostat_data.update({'hysteresis': thermostat.hysteresis})
                thermostat_data.update({'url_safe_key': thermostat.key.urlsafe()})

                # Aggiungo l'elemento corrente alla lista
                list.append(copy.deepcopy(thermostat_data))
        return list

    @ThermostHouseRequestHandler.login_required
    def get(self):

        """ Visualizza le informazioni dei termostati, se già aggiunti. Altrimenti permette di
        aggiungerne uno
        """
        user = self.check_user_logged_in
        thermostats = Users.get_owned_thermostats(user)
        list = []
        # Devo visualizzare tutti termostati
        list = self.set_thermostat_data(thermostats)  # Carico correttamente i valori nella list

        # Carico la pagina con i parametri degli utenti
        self.render('thermostat-page/thermostat-page.html', thermostats_data=list)


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
                therm_key = therm.put()

                # therm.put() does not create anymore new thermostat table. a thermsotat is visible from user table
                user.thermostat.append(therm_key)
                user.put()
                # latency introduced in order to guarantee the eventual consistency of ndb
                import time
                time.sleep(0.5)
                self.redirect('/thermostat')
            except Exception as ex:
                error_msg = "Exception '{ex}', {ex_type} "
                logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
                self.render('communication/error.html', mail=conf['EMAIL_RECEIVER'])
        else:
            # La localizzazione non è riuscita, mostro un messaggio di errore
            self.render("communication/bad_location.html")


class SetThermostat(ThermostHouseRequestHandler):
    @ThermostHouseRequestHandler.login_required
    def get(self):
        therm_safe_key = self.request.get('id')
        template_values = {
            'therm_safe_key': therm_safe_key
        }
        self.render("thermostat-page/set-thermostat.html", **template_values)

    @ThermostHouseRequestHandler.login_required
    def post(self):
        therm_safe_key = self.request.get('id')
        # retrieve the real key from the urlsafe
        key = ndb.Key(urlsafe=therm_safe_key)

        # retrieve the thermostat id
        ident = key.id()
        thermostat = Thermostats.get_by_id(int(ident))  # because recipe_id was a string

        # taken the entity of the thermostat to update
        try:
            thermostat.temperature = float(self.request.get('temperature'))
            thermostat.hysteresis = float(self.request.get('hysteresis'))
            thermostat.put()
            # latency introduced in order to guarantee the eventual consistency of ndb
            import time
            time.sleep(0.5)
        except Exception as ex:
            error_msg = "Exception '{ex}', {ex_type}"
            logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
            self.render('/communication/error.html', mail=conf['EMAIL_RECEIVER'])

        self.redirect("/thermostat")


class DeleteThermostat(ThermostHouseRequestHandler):
    @ThermostHouseRequestHandler.login_required
    def get(self):
        therm_safe_key = self.request.get('id')
        # retrieve the real key from the urlsafe
        key = ndb.Key(urlsafe=therm_safe_key)

        # get the thermostat entity
        thermostat = key.get()
        # delete the thermostat
        thermostat.key.delete()

        # update the list of thermostats owned by the user
        user = self.check_user_logged_in
        list = []
        for thermostat in user.thermostat:
            if key != thermostat:
                list.append(thermostat)
        user.thermostat = list

        import time
        time.sleep(0.5)
        self.redirect("/thermostat")


class ThermostatDeviceRequest(ThermostHouseRequestHandler):
    def get(self):
        string = "{'DeviceId':123453,'SequenceNumber':13,'RequestType':'standard','MessageId':'ilMioFantasticoId'," \
                 "'Settings':{'TargetTemperature':10,'Hysteresis':20,'ColdDelay':20},'CurrentState':{'Temperature':10,'ColdState':'OFF','HotState':'OFF'}}"
        import ast
        data = ast.literal_eval(string)
        if not data['DeviceId'] or not data['SequenceNumber'] or not data['RequestType'] \
                or not data['MessageId'] or not data['Settings'] or not data['CurrentState'] \
                or not data['Settings']['TargetTemperature'] or not data['Settings']['Hysteresis'] \
                or not data['Settings']['ColdDelay'] or not data['CurrentState']['Temperature'] \
                or not data['CurrentState']['ColdState'] or not data['CurrentState']['HotState']:
            json_response_temp = {
                'Response': 'False'
            }
            print "errore"
        return

    def post(self):
        data = self.request.body
        # data = urllib2.unquote(data).decode('utf8') no more needed
        data = json.loads(data)

        json_response = {}
        if not data['DeviceId'] or not data['SequenceNumber'] or not data['RequestType'] \
                or not data['MessageId'] or not data['Settings'] or not data['CurrentState'] \
                or not data['Settings']['TargetTemperature'] or not data['Settings']['Hysteresis'] \
                or not data['Settings']['ColdDelay'] or not data['CurrentState']['Temperature'] \
                or not data['CurrentState']['ColdState'] or not data['CurrentState']['HotState']:
            json_response_temp = {
                'Response': 'False'
            }
            json_response.update(json_response_temp)
        else:
            device_id = data['DeviceId']
            sequence_number = data['SequenceNumber']
            request_type = data['RequestType']
            message_id = data['MessageId']
            settings = data['Settings']
            current_state = data['CurrentState']

            json_response_temp = {
                'DeviceId': device_id,
                'SequenceNumber': sequence_number,
                'RequestType': request_type,
                'MessageId': message_id,
                'Settings': settings,
                'CurrentState': current_state,
                'Response': 'True'
            }
            json_response.update(json_response_temp)

        self.json_response(status_code=200, **json_response)
