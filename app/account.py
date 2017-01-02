#!/usr/bin/env python
# -*- coding:utf-8 -*-

from conf.configuration_reader import conf, secret
from framework.request_handler import ThermostHouseRequestHandler
from cloudstorage import cloudstorage_api
from google.appengine.api import blobstore, images
from models.recipes import Recipes
import logging
import urllib2
from models.users import Users
from google.appengine.ext import ndb
import copy
import base64


class UserAccount(ThermostHouseRequestHandler):
    def set_usr_data(self, authenticated_user):
        if authenticated_user is None:
            return None

        usr_data = {}

        usr_data.update({'username': authenticated_user.username})
        # if authenticated_user.address:
        #     usr_data.update({'city': authenticated_user.address.city})
        # else:
        #     usr_data.update({'city': None})

        if authenticated_user.image and not authenticated_user.google:
            encoded_image = base64.b64encode(authenticated_user.image)
            src = "data:image/gif;base64," + encoded_image
            usr_data.update({'image': src})
        else:
            usr_data.update({'image': authenticated_user.image})

        # if authenticated_user.impianto:
        #     usr_data.update({'plant': authenticated_user.impianto.tipo})
        # else:
        #     usr_data.update({'plant': None})

        usr_data.update({'email': authenticated_user.email})

        usr_data.update({'urlsafeKey': authenticated_user.key.urlsafe()})

        return usr_data

    @ThermostHouseRequestHandler.login_required  # restrict access for not logged users
    def get(self):
        # get the user information
        user = self.check_user_logged_in
        try:
            user_data = self.set_usr_data(user)
            tpl_values = {
                'user_data': user_data,
            }
            # Carico la pagina con i parametri degli utenti
            self.render('account/user_profile.html', **tpl_values)
        except Exception as ex:
            error_msg = "Exception '{ex}', {ex_type} "
            logging.error(error_msg.format(ex=ex, ex_type=type(ex)))
            self.render('communication/error.html', mail=conf['EMAIL_RECEIVER'])
            # user_id = self.check_user_logged_in.key.id()

            #     user = self.request.get('user')
            #
            #     reconstructed_key = ndb.Key(urlsafe=user)
            #
            #     if reconstructed_key != autenticated_user_key:
            #         # Eseguo la ricerca
            #         qry = ndb.gql('SELECT * FROM Users where __key__ IN :1', [reconstructed_key])
            #         list = self.set_usr_data(qry, autenticated_user_key)  # Carico correttamente i valori nella list
            #         autenticated_user = None
            #
            # # js_user_data = json.dumps(list)
            #
            # # Carico la pagina con i parametri degli utenti
            # self.render('account/user_profile.html', autenticated_user=self.set_auth_usr_data(autenticated_user),
            #             usr_data=list)


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
