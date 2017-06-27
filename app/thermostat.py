#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
from os import environ

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

        list = []

        for thermostat in qry:
            if not thermostat:
                pass
            else:
                # Clean the dictionary
                thermostat_data = {}

                # thermostat_data.update({'user': thermostat.user})
                thermostat_data.update({'name': thermostat.name})
                thermostat_data.update({'address': thermostat.address})
                thermostat_data.update({'temperature': thermostat.temperature})
                thermostat_data.update({'hysteresis': thermostat.hysteresis})
                thermostat_data.update({'cold_delay': thermostat.cold_delay})
                thermostat_data.update({'ID': thermostat.key.id()})

                if not environ['SERVER_SOFTWARE'].startswith('Development'):
                    from app.plot import plot
                    chart = plot(thermostat)
                    thermostat_data.update({'chart': chart})
                # Add current item into the list
                # list.append(copy.deepcopy(thermostat_data))
                list.append(thermostat_data)
        return list

    @ThermostHouseRequestHandler.login_required
    def get(self):

        """
        Show the info of all thermostat owned
        """
        user = self.check_user_logged_in
        thermostats = Users.get_owned_thermostats(user)

        # Show all thermostat data
        list = self.set_thermostat_data(thermostats)  # Carico correttamente i valori nella list

        if self.request.get('exported'):
            return self.render('thermostat-page/thermostat-page.html', thermostats_data=list,
                               exported=int(self.request.get('exported')))

        # render the page
        return self.render('thermostat-page/thermostat-page.html', thermostats_data=list)


class CreateThermostat(ThermostHouseRequestHandler):
    @ThermostHouseRequestHandler.login_required
    def get(self):
        self.render("thermostat-page/create-thermostat.html")

    @ThermostHouseRequestHandler.login_required
    def post(self):
        user = self.check_user_logged_in

        # collection of address data
        address = Address()
        address.province = self.request.get('province')
        try:
            address.zip_code = int(self.request.get('zip_code'))
            address.number = int(self.request.get('number'))
            address.region = self.request.get('region')
            address.street = self.request.get('street')
            address.city = self.request.get('city')
        except ValueError:
            # managed in client side
            pass

        # call geo function on an address
        status_geocode = address.geocode()

        if status_geocode == 0:
            # localized successfully, continue

            # Collection of thermostat data
            # therm = Thermostats()
            try:
                name = self.request.get('nameTH')
                plain_password = self.request.get('passwordTH')
                Thermostats.add_new_thermostat(name, plain_password, address, user.key)

                self.redirect('/thermostat')
            except Exception as ex:
                error_msg = "Exception '{ex}', {ex_type} "
                logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
                self.render('communication/error.html', mail=conf['EMAIL_RECEIVER'])
        else:
            # Localization failed, show an error message
            self.render("communication/bad_location.html")


class SetThermostat(ThermostHouseRequestHandler):
    @ThermostHouseRequestHandler.login_required
    def post(self):

        therm_id = self.request.get('id')
        temp = float(self.request.get('temp'))
        hyst = float(self.request.get('hyst'))
        cold_delay = int(self.request.get('cold_delay'))

        thermostat = Thermostats.get_by_id(int(therm_id))
        # taken the entity of the thermostat to update
        try:
            thermostat.temperature = round(temp, 1)
            thermostat.hysteresis = round(hyst, 1)
            thermostat.cold_delay = cold_delay
            thermostat.put()

        except Exception as ex:
            error_msg = "Exception '{ex}', {ex_type}"
            logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
            self.render('/communication/error.html', mail=conf['EMAIL_RECEIVER'])

        self.redirect("/thermostat")


class DeleteThermostat(ThermostHouseRequestHandler):
    @ThermostHouseRequestHandler.login_required
    def post(self):
        therm_id = int(self.request.get('id'))

        # get the thermostat entity
        thermostat = Thermostats.get_by_id(therm_id)

        # delete the thermostat
        thermostat.key.delete()

        self.redirect("/thermostat")
