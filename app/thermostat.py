#!/usr/bin/env python
# -*- coding:utf-8 -*-

from framework.request_handler import ThermostHouseRequestHandler
from google.appengine.api import search
from models.recipes import Recipes
from models.users import Users
import base64
import copy

class RecipePage(ThermostHouseRequestHandler):
    @ThermostHouseRequestHandler.login_required
    def get(self):
        """ Visualizza le informazioni dei termostati, se già aggiunti. Altrimenti permette di
        aggiungerne uno
        """
        user = self.request.get('user')

        # Utente autenticato
        autenticated_plant_user, autenticated_plant_user_key = self.get_auth_user()
        list = []

        if user == "":
            # Devo visualizzare tutti gli impianti

            # Impianti
            qry = Users.get_users_plants()
            list = self.set_plant_data(qry, autenticated_plant_user_key)  # Carico correttamente i valori nella list
        else:
            # E' stato specificato un utente tramite URL, eseguo la ricerca
            reconstructed_key = ndb.Key(urlsafe=utente)

            if reconstructed_key != autenticated_plant_user_key:
                # Eseguo la ricerca
                qry = ndb.gql('SELECT * FROM Utente where __key__ IN :1', [reconstructed_key])
                list = self.set_plant_data(qry, autenticated_plant_user_key)  # Carico correttamente i valori nella list
                autenticated_plant_user = None

        # Carico la pagina con i parametri degli utenti
        self.render('impianto_profile.html',
                    autenticated_plant=self.set_auth_plant_data(autenticated_plant_user),
                    plant_data=list)
