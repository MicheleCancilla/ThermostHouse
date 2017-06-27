#!/usr/bin/env python
# -*- coding:utf-8 -*-


from webapp2 import Route
from webapp2 import WSGIApplication

from app.decorator import decorator

app = WSGIApplication(
    routes=[
        Route('/', handler='app.home.Home'),
        Route('/home', handler='app.home.Home'),

        Route('/register', handler='app.register.RegisterUser'),
        Route('/register_complete', handler='app.register.ConfirmRegistration'),
        Route('/account/<user_id:[0-9]+>/confirm/<confirmation_code:[a-z0-9]{32}>', handler='app.register.ConfirmUser'),

        Route('/login', handler='app.login.LoginUser'),
        Route('/google_login', handler='app.login_manager.GoogleLogin'),
        Route(decorator.callback_path, handler=decorator.callback_handler()),
        Route('/facebook_login', handler='app.login_manager.FacebookLogin'),
        Route('/logout', handler='app.login_manager.LogOut'),

        Route('/thermostat', handler='app.thermostat.ThermostatPage'),
        Route('/create_thermostat', handler='app.thermostat.CreateThermostat'),
        Route('/set_thermostat', handler='app.thermostat.SetThermostat'),
        Route('/set_thermostat', handler='app.thermostat.SetThermostat'),
        Route('/delete_thermostat', handler='app.thermostat.DeleteThermostat'),

        Route('/account', handler='app.account.UserAccount'),
        Route('/account/api', handler='app.account.Api'),
        Route('/edit_profile', handler='app.edit_profile.EditProfile'),
        Route('/change_password', handler='app.edit_profile.ChangePassword'),

        Route('/info', handler='app.info.Info'),
        Route('/api', handler='app.api.Api'),
        Route('/api/get_temp', handler='app.api.ThermostatTempRequest'),
        Route('/api/device', handler='app.api.ThermostatDeviceRequest'),
        Route('/device', handler='app.api.ThermostatDeviceRequest'),

        Route('/export', handler='app.export_temp.ExportToSheets'),
    ])
