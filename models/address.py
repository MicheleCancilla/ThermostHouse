# -*- coding: utf-8 -*-


"""
    Modello INDIRIZZO per il datastore: INDIRIZZO è una structuredProperty di UTENTE. In questo file viene anche
    definita la funzione di geolocalizzazione che effettua la chiamata all'API Geocode di Google
"""

from google.appengine.ext import ndb
import urllib
import json
from conf.configuration_reader import conf


class Address(ndb.Model):
    street = ndb.StringProperty(required=True)
    number = ndb.IntegerProperty(required=True)
    city = ndb.StringProperty(required=True)
    province = ndb.StringProperty(required=True,
                                  choices=['AG', 'AL', 'AN', 'AO', 'AQ', 'AR', 'AP', 'AT', 'AV', 'BA', 'BT', 'BL',
                                           'BN', 'BG', 'BI', 'BO', 'BZ', 'BS', 'BR', 'CA', 'CL', 'CB', 'CE', 'CT',
                                           'CZ', 'CH', 'CO', 'CS', 'CR', 'KR', 'CN', 'EN', 'FM', 'FE', 'FI', 'FG',
                                           'FC', 'FR', 'GE', 'GO', 'GR', 'IM', 'IS', 'SP', 'LT', 'LE', 'LC', 'LI',
                                           'LO', 'LU', 'MC', 'MN', 'MS', 'MT', 'ME', 'MI', 'MO', 'MB', 'NA', 'NO',
                                           'NU', 'OR', 'PD', 'PA', 'PR', 'PV', 'PG', 'PU', 'PE', 'PC', 'PI', 'PT',
                                           'PN', 'PZ', 'PO', 'RG', 'RA', 'RC', 'RE', 'RI', 'RN', 'RM', 'RO', 'SA',
                                           'SS', 'SV', 'SI', 'SR', 'SO', 'TA', 'TE', 'TR', 'TO', 'TP', 'TN', 'TV',
                                           'TS', 'UD', 'VA', 'VE', 'VB', 'VC', 'VR', 'VV', 'VI', 'VT'])
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
            Metodo per il calcolo delle coordinare geografiche di un indirizzo. Il metodo fa uso dell'API di
            geolocalizzazione di Google: GEOCODE.

        """

        # Costruisco l'indirizzo in base alle informazioni ricevute
        address = self.street + " " + str(self.number) + ", " + str(self.zip_code) + " " + str(self.city) + " " + str(
            self.province) + ", " + str(self.region) + ", " + str(self.nation)

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
            # Non è stato possibile effettuare la richiesta a Google
            return 1
        elif status == 'ZERO_RESULTS':
            # Non è stata trovata alcuna corrispondenza
            return 1
        elif status == 'OVER_QUERY_LIMIT':
            # Superato il limite giornaliero di richieste
            return 1
        elif status == 'REQUEST_DENIED':
            # Indicates that your request was denied, generally because of lack of an invalid key parameter
            return 1
        elif status == 'INVALID_REQUEST':
            # Errore, non sono riuscito a localizzare l'utente
            return 1
        elif status == 'OK':
            # Estrazione delle informazioi di latitudine e longitudine dall'oggetto RESULTS, se vengono individuati più punti sulla mappa si considera solo il primo
            lat = result["results"][0]["geometry"]["location"]["lat"]
            lng = result["results"][0]["geometry"]["location"]["lng"]

        self.latlng = ndb.GeoPt(lat, lng)
        return 0
