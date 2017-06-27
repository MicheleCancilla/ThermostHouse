#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Module for the registered temperature export in google sheets
"""
import datetime
import logging

from oauth2client import client

from app.decorator import sheets_decorator, sheets_service
from framework.request_handler import ThermostHouseRequestHandler
from models.thermostats import Thermostats


class ExportToSheets(ThermostHouseRequestHandler):
    @ThermostHouseRequestHandler.login_required
    @sheets_decorator.oauth_aware
    def get(self):
        if sheets_decorator.has_credentials():
            thermostat_id = None
            try:

                thermostat_id = int(self.request.get('id'))

                thermostat = Thermostats.get_by_id(thermostat_id)

                temperatures = thermostat.history
                # from models.historicals import Historicals
                # history = Historicals()
                # history.temperature = 12.4
                # history.mode = 'Heat'
                # thermostat.history.append(history)
                # thermostat.put()
                # return
                row = 0
                data = []
                for temp in reversed(temperatures):
                    data.append(
                        {
                            "startRow": row,
                            "startColumn": 0,
                            "rowData":
                                {
                                    "values":
                                        {
                                            "userEnteredValue":
                                                {
                                                    "stringValue": str(temp.timestamp)
                                                },
                                        }
                                },
                        })
                    data.append(
                        {
                            "startRow": row,
                            "startColumn": 1,
                            "rowData":
                                {
                                    "values":
                                        {
                                            "userEnteredValue":
                                                {
                                                    "numberValue": float(temp.temperature)
                                                },
                                        }
                                },
                        })
                    data.append(
                        {
                            "startRow": row,
                            "startColumn": 2,
                            "rowData":
                                {
                                    "values":
                                        {
                                            "userEnteredValue":
                                                {
                                                    "stringValue": str(temp.mode)
                                                },
                                        }
                                },
                        })
                    row += 1
                    if row >= 1000:
                        break

                body = {
                    'properties':
                        {
                            'title': str(thermostat_id) + " " + str(datetime.datetime.now())
                        },
                    'sheets':
                        {
                            'data': data,
                        },
                }

                sheets_service.spreadsheets().create(body=body).execute(http=sheets_decorator.http())

            except client.AccessTokenRefreshError as ex:
                error_msg = "Exception: Access Token Refresh Error, retry to login, {ex_type}"
                logging.error(error_msg.format(ex_type=type(ex)))
                self.redirect('/home')

            return self.redirect("/thermostat?exported=%s" % thermostat_id)

        else:
            url = sheets_decorator.authorize_url()

            # redirect to google authorize page
            return self.redirect(url)
