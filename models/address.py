# -*- coding: utf-8 -*-


"""
    Address model: address is an user's structuredProperty. Geolocation (Google API) is also defined here
"""

import json
import urllib

from google.appengine.ext import ndb

from conf.configuration_reader import conf


class Address(ndb.Model):
    street = ndb.StringProperty(required=True)
    number = ndb.IntegerProperty(required=True)
    city = ndb.StringProperty(required=True)
    province = ndb.StringProperty(required=True,
                                  choices=['Agrigento', 'Alessandria', 'Ancona', 'Aosta', 'Aquila', 'Arezzo',
                                           'Ascoli Piceno', 'Asti', 'Avellino', 'Bari', 'Barletta', 'Belluno',
                                           'Benevento', 'Bergamo', 'Biella', 'Bologna', 'Bolzano', 'Brescia', 'Bindisi',
                                           'Cagliari', 'Caltanissetta', 'Campobasso', 'Caserta', 'Catania',
                                           'Catanzaro', 'Chieti', 'Como', 'Cosenza', 'Cremona', 'Crotone', 'Cuneo',
                                           'Enna', 'Fermo', 'Ferrara', 'Firenze', 'Foggia',
                                           'Forlì-Cesena', 'Frosinone', 'Genova', 'Gorizia', 'Grosseto', 'Imperia',
                                           'Isernia', 'La Spezia', 'Latina', 'Lecce', 'Lecco', 'Livorno',
                                           'Lodi', 'Lucca', 'Macerata', 'Mantova', 'Massa-Carrara', 'Matera', 'Messina',
                                           'Milano', 'Modena', 'Monza e Brienza', 'Napoli', 'Novara',
                                           'Nuoro', 'Oristano', 'Padova', 'Palermo', 'Parma', 'Pavia', 'Perugia',
                                           'Pesaro e Urbino', 'Pescara', 'Piacenza', 'Pisa', 'Pistoia',
                                           'Pordenone', 'Potenza', 'Prato', 'Ragusa', 'Ravenna', 'Reggio Calabria',
                                           'Reggio Emilia', 'Rieti', 'Rimini', 'Roma', 'Rovigo', 'Salerno',
                                           'Sassari', 'Savona', 'Siena', 'Siracusa', 'Sondrio', 'Taranto', 'Teramo',
                                           'Trani', 'Torino', 'Trapani', 'Trento', 'Treviso',
                                           'Trieste', 'Udine', 'Varese', 'Venezia', 'Verbano', 'Vercelli', 'Verona',
                                           'Vibo Valentia', 'Vicenza', 'Viterbo'])
    region = ndb.StringProperty(required=True,
                                choices=['Abruzzo', 'Basilicata', 'Calabria', 'Campania', 'Emilia-Romagna',
                                         'Friuli-Venezia Giulia', 'Lazio', 'Liguria', 'Lombardia', 'Marche', 'Molise',
                                         'Piemonte', 'Puglia', 'Sardegna', 'Sicilia', 'Toscana', 'Trentino-Alto Adige',
                                         'Umbria', 'Valle d\'Aosta', 'Veneto'])
    latlng = ndb.GeoPtProperty(required=True)
    zip_code = ndb.IntegerProperty(required=True)
    nation = ndb.StringProperty(required=True, default='Italy')

    def geocode(self, **geo_args):
        """
            Function useful for retrieve the geo coord of an address.
        """

        # Build the address
        # address = self.street + " " + str(self.number) + ", " + str(self.zip_code) + " " + str(self.city) + " " + str(
        #     self.province) + ", " + str(self.region) + ", " + str(self.nation)
        address = str(self.province) + ", " + str(self.region) + ", " + str(self.nation)
        print address
        geo_args.update({
            'address': address
        })

        url = conf['GEOCODE_BASE_URL'] + '?' + urllib.urlencode(geo_args)

        try:
            result = json.load(urllib.urlopen(url))
            status = result["status"]
        except:
            status = None
        finally:
            pass

        if status is None:
            # Request failed
            return 1
        elif status == 'ZERO_RESULTS':
            # No match found
            return 1
        elif status == 'OVER_QUERY_LIMIT':
            # Number of requests exceeded
            return 1
        elif status == 'REQUEST_DENIED':
            # Indicates that your request was denied, generally because of lack of an invalid key parameter
            return 1
        elif status == 'INVALID_REQUEST':
            # Error, localization failed
            return 1
        elif status == 'OK':
            # extraction of lat and lng information
            lat = result["results"][0]["geometry"]["location"]["lat"]
            lng = result["results"][0]["geometry"]["location"]["lng"]

        self.latlng = ndb.GeoPt(lat, lng)
        return 0
