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
