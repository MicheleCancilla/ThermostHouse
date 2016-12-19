#!/usr/bin/env python
# -*- coding:utf-8 -*-


from framework.request_handler import ThermostHouseRequestHandler
from cloudstorage import cloudstorage_api
from google.appengine.api import blobstore, images
from models.recipes import Recipes
from models.users import Users
from google.appengine.ext import ndb
import copy
import base64


class UserAccount(ThermostHouseRequestHandler):
    def set_auth_usr_data(self, authenticated_user):
        if authenticated_user is None:
            return None

        usr_data = {}

        usr_data.update({'name': authenticated_user.username})
        if authenticated_user.address:
            usr_data.update({'citta': authenticated_user.address.citta})
        else:
            usr_data.update({'citta': None})

        if authenticated_user.image:
            encoded_image = base64.b64encode(authenticated_user.immagine)
            src = "data:image/gif;base64," + encoded_image
            usr_data.update({'image': src})
        else:
            usr_data.update({'image': authenticated_user.image})

        # if authenticated_user.impianto:
        #     usr_data.update({'plant': authenticated_user.impianto.tipo})
        # else:
        #     usr_data.update({'plant': None})

        usr_data.update({'mail': authenticated_user.email})

        usr_data.update({'urlsafeKey': authenticated_user.key.urlsafe()})

        return usr_data

    def set_usr_data(self, qry, auth_usr_key):
        if qry is None:
            return []

        # Preparo i valori caricandoli in un dizionario
        list = []
        usr_data = {}
        for data in qry:
            if data.key == auth_usr_key:
                # L'utente autenticato è un caso a parte, non lo devo gestire in questa situazione
                pass
            else:
                # Vuoto il dizionario per il giro successivo
                usr_data.clear()

                usr_data.update({'name': data.username})
                if data.address:
                    usr_data.update({'citta': data.address.citta})
                else:
                    usr_data.update({'citta': None})

                if data.image:
                    encoded_image = base64.b64encode(data.immagine)
                    src = "data:image/gif;base64," + encoded_image
                    usr_data.update({'image': src})
                else:
                    usr_data.update({'image': data.image})

                # if data.impianto:
                #     usr_data.update({'plant': data.impianto.tipo})
                # else:
                #     usr_data.update({'plant': None})
                usr_data.update({'mail': data.email})

                usr_data.update({'urlsafeKey': data.key.urlsafe()})

                # Aggiungo l'elemento corrente alla lista
                list.append(copy.deepcopy(usr_data))

        return list

    @ThermostHouseRequestHandler.login_required  # restrict access for not logged users
    def get(self):
        # user_id = self.check_user_logged_in.key.id()
        # recipes = Recipes.get_all_recipes_by_user(user_id)
        #
        # tpl_values = {
        #     'recipes': recipes,
        #
        # }
        # self.render('account/home.html', **tpl_values)
        user = self.request.get('user')

        # Utente autenticato
        autenticated_user, autenticated_user_key = self.get_auth_user()
        list = []

        if user == "":
            # Devo visualizzare tutti gli utenti iscritti al servizio

            # Utenti
            qry = Users.get_users()
            list = self.set_usr_data(qry, autenticated_user_key)  # Carico correttamente i valori nella list
        else:
            # E' stato specificato un utente tramite URL, eseguo la ricerca
            reconstructed_key = ndb.Key(urlsafe=user)

            if reconstructed_key != autenticated_user_key:
                # Eseguo la ricerca
                qry = ndb.gql('SELECT * FROM Utente where __key__ IN :1', [reconstructed_key])
                list = self.set_usr_data(qry, autenticated_user_key)  # Carico correttamente i valori nella list
                autenticated_user = None

        # js_user_data = json.dumps(list)

        # Carico la pagina con i parametri degli utenti
        self.render('user_profile.html', autenticated_user=self.set_auth_usr_data(autenticated_user), usr_data=list)


class PostRecipe(ThermostHouseRequestHandler):
    @ThermostHouseRequestHandler.login_required
    def get(self):
        self.render('/account/post_recipe.html')

    @ThermostHouseRequestHandler.login_required
    def post(self):
        user_key = self.check_user_logged_in.key  # retrieve user key
        title = self.request.get('title')
        cuisine = self.request.get('cuisine')
        difficulty = self.request.get('difficulty')
        prep_time = self.request.get('prep_time')
        cook_time = self.request.get('cooking_time')
        ingredients = self.request.get('ingredients')
        directions = self.request.get('directions')
        photo = self.request.POST['image']

        saved_photo = self.save_image(photo, user_key)

        Recipes.add_new_recipe(
            title=title,
            cuisine=cuisine,
            difficulty=difficulty,
            prep_time=prep_time,
            cook_time=cook_time,
            ingredients=ingredients,
            directions=directions,
            user_key=user_key,
            photo_key=saved_photo['blobstore_key'],
            photo_url=saved_photo['serving_url'],
        )

        self.redirect('/account')

    @classmethod
    def save_image(cls, photo, user_key):
        img_title = photo.filename
        img_content = photo.file.read()
        img_type = photo.type

        # xenov-search.appspot.com is the bucket
        cloud_storage_path = '/gs/xenov-search.appspot.com/%s/%s' % (user_key.id(), img_title)

        blobstore_key = blobstore.create_gs_key(cloud_storage_path)

        cloud_storage_file = cloudstorage_api.open(
            filename=cloud_storage_path[3:],
            mode='w',
            content_type=img_type
        )
        cloud_storage_file.write(img_content)
        cloud_storage_file.close()

        blobstore_key = blobstore.BlobKey(blobstore_key)  # extract the url
        serving_url = images.get_serving_url(blobstore_key)

        return {
            'serving_url': serving_url,
            'blobstore_key': blobstore_key
        }
