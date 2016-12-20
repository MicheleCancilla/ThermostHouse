#!/usr/bin/env python
# -*- coding:utf-8 -*-
from google.appengine.ext import ndb
from models.address import Address


class Thermostats(ndb.Model):
    user = ndb.KeyProperty(kind='Users')
    name = ndb.StringProperty(required=True)
    home = ndb.StructuredProperty(Address, required=True)
    temperature = ndb.FloatProperty(default=0.0)
    hysteresis = ndb.FloatProperty(default=0.0)

    @classmethod
    def add_new_thermostat(cls, name, home, temperature, hysteresis, user_key=None):
        user_id = ''

        if user_key:
            user_id = str(user_key.id())

        thermostat_key = cls(
            user=user_key,
            name=name,
            home=home,
            temperature=float(temperature),
            hysteresis=float(hysteresis),
        ).put()

        # index = search.Index('thermostats')
        # doc = search.Document(
        #     doc_id=str(thermostat_key.id()),
        #     fields=[
        #         search.TextField(name='user_id', value=user_id),
        #         search.TextField(name='name', value=name),
        #         search.NumberField(name='temperature', value=float(temperature)),
        #         search.NumberField(name='hysteresis', value=float(hysteresis)),
        #     ]
        # )
        #
        # index.put(doc)


