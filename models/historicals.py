#!/usr/bin/env python
# -*- coding:utf-8 -*-

from google.appengine.ext import ndb


class Historicals(ndb.Model):
    timestamp = ndb.DateTimeProperty(auto_now_add=True)  # DateTime of measurement
    temperature = ndb.FloatProperty(required=True)
    mode = ndb.StringProperty(choices=['Cold', 'Heat', 'None'], required=True)  # kind of mode
