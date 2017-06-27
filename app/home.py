#!/usr/bin/env python
# -*- coding:utf-8 -*-
from framework.request_handler import ThermostHouseRequestHandler
from models.thermostats import Thermostats
from conf.configuration_reader import secret
import json
import copy


class Home(ThermostHouseRequestHandler):
    def get(self):
        # Retrieve all the existing thermostats
        qry = Thermostats.get_thermostats()
        mylist = []
        supp_dict = {}
        my_data = {'latlng': mylist}

        for data in qry:
            # Clear the dictionary
            supp_dict.clear()
            found = 0
            if data.address is not None:
                # coord_list contains the province already inserted
                coord_list = my_data.get('latlng')
                for elem in coord_list:
                    if data.address.latlng.lon == elem['lng'] and data.address.latlng.lat == elem['lat']:
                        # element already inserted, retrieve his index
                        index = coord_list.index(elem)
                        temp = coord_list[index]
                        temp['occurrences'] += 1
                        coord_list[index] = temp
                        found = 1
                if not found:
                    # first time that this province appears
                    supp_dict.update({'lat': data.address.latlng.lat})
                    supp_dict.update({'lng': data.address.latlng.lon})
                    supp_dict.update({'occurrences': 1})
                    my_data['latlng'].append(copy.deepcopy(supp_dict))
            else:
                # no valid address, address to not show
                pass

        # Add Google API for map creation in JavaScript
        my_data.update({'mapKey': secret['API_KEY']})

        my_data.update({'fb_key': secret['FACEBOOK_APP_ID']})


        js_data = json.dumps(my_data)

        return self.render_json('home/home.html', js_data)
