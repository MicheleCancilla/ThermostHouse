#!/usr/bin/env python
# -*- coding:utf-8 -*-
from framework.request_handler import ThermostHouseRequestHandler
from models.users import Users
import json
import copy


class Home(ThermostHouseRequestHandler):
    def get(self):
        qry = Users.get_users()
        mylist = []
        supp_dict = {}
        my_data = {'latlng': mylist}
        for data in qry:
            # Vuoto il dizionario per il giro successivo
            supp_dict.clear()

            if data.address is not None:

                # Carico i nuovi valori
                supp_dict.update({'lat': data.address.latlng.lat})
                supp_dict.update({'lng': data.address.latlng.lon})
                supp_dict.update({'name': data.username})
                # La chiave (codificata tramite il metodo urlsafe) verrà utilizzata per effettuare la ricerca dell'utente quando si clicca sul marker associato nella mappa
                supp_dict.update({'userID': data.key.urlsafe()})
                my_data['latlng'].append(copy.deepcopy(supp_dict))

            else:
                pass
                # L'utente corrente non ha un indirizzo valido, non lo carico sulla mappa

        # my_data = [{"lat": 44.45645, "lng": 11.34534, "name":"Foo"},{"lat": 45.45645, "lng": 20.0000, "name":"my"}]
        # js_data = json.dumps([-25.323, 44.444])

        # Aggiungo ai dati da passare a JavaScript la chiave per l'API di Google per la creazione della mappa
        # my_data.update({'mapKey': secret['API_KEY']})
        # my_data.update({'weatherKey': secret['OPENWEATHER_KEY']})

        js_data = json.dumps(my_data)

        self.render_json('home/home.html', js_data)
