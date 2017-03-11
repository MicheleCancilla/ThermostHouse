#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import urllib2

from google.appengine.api import users
from oauth2client import client

from app.decorator import decorator, service
from conf.configuration_reader import conf
from framework.request_handler import ThermostHouseRequestHandler
from models.users import Users

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class ExportToDrive(ThermostHouseRequestHandler):
    def get(self):
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        # drive = GoogleDrive(gauth)
        #
        # test_file = drive.CreateFile({'title': 'testfile.xlsx'})
        # test_file.SetContentFile('testfile.xlsx')
        # test_file.Upload({'convert': True})
        return
