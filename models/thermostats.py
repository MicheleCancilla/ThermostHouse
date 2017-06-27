#!/usr/bin/env python
# -*- coding:utf-8 -*-
from google.appengine.ext import ndb
from models.address import Address
from models.historicals import Historicals


class Thermostats(ndb.Model):
    name = ndb.StringProperty(required=True)
    plain_password = ndb.StringProperty(required=True)

    sequence_number = ndb.IntegerProperty(default=0)
    address = ndb.StructuredProperty(Address, required=True)
    temperature = ndb.FloatProperty(default=0.0)
    hysteresis = ndb.FloatProperty(default=0.0)
    cold_delay = ndb.IntegerProperty(default=3)  # delay in minutes if our device use an air pump

    # key of the user, used to simulate one-to-many relationship
    owner = ndb.KeyProperty(kind='Users', repeated=False, required=True)
    history = ndb.StructuredProperty(Historicals, repeated=True)

    @classmethod
    def add_new_thermostat(cls, name, plain_password, address, user_key):

        cls(
            owner=user_key,
            name=name,
            address=address,
            plain_password=plain_password
        ).put()

    @classmethod
    def get_thermostats(cls):
        """Return all existing thermostats"""
        qry = cls.query()
        return qry

    @classmethod
    def get_thermostats_by_owner(cls, owner_key):
        """Return all thermostats finding them by owner key"""
        if not owner_key:
            return None
        else:
            return ndb.gql("SELECT * FROM Thermostats where owner = :1", owner_key)
