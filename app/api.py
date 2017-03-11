#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
from hashlib import sha256

from framework.request_handler import ThermostHouseRequestHandler
from models.historicals import Historicals
from models.thermostats import Thermostats
from models.users import Users


class ThermostatDeviceRequest(ThermostHouseRequestHandler):
    def get(self):
        password = '123password321'
        hashed_pwd = sha256(str('0') + password + str(
            '0')).hexdigest()
        string = "{'DevId':'5066549580791808','SeqNumber':'4','RequestType':'std','Settings':{'TargetTemp':10,'Hyst':10,'ColdDelay':10},'CurState':{'Temp':100,'Mode':'Heat'},'Sign':'c97b8537b22e925f005b871954c9904cd3d308e78c14349e014933e983b3ec3b'}"
        import ast
        data = ast.literal_eval(string)

        json_response = {}
        try:
            therm_id = int(data['DevId'])
            sequence_number = int(data['SeqNumber'])
            request_type = data['RequestType']
            sign = data['Sign']
            settings_target_temp = float(data['Settings']['TargetTemp'])
            settings_hysteresis = float(data['Settings']['Hyst'])
            settings_cold_delay = int(data['Settings']['ColdDelay'])
            current_state_temp = float(data['CurState']['Temp'])
            current_state_mode = str(data['CurState']['Mode'])
            if therm_id is not None:
                # get the owner information from thermostat indicated by therm_id
                therm = Thermostats.get_by_id(therm_id)
                if therm is None:
                    # case 2: bad device id
                    json_response_temp = {
                        'Response': 'Bad',
                        'ErrMsg': 'BadDevId',
                        'ErrId': 2,
                    }
                    json_response.update(json_response_temp)
                else:
                    # get the information about owner. Password is needed
                    user = Users.get_by_id(therm.owner.id())

                    if sequence_number <= therm.sequence_number:
                        # Case 3: Bad sequence number
                        therm.sequence_number += 1
                        json_response_temp = {
                            'Response': 'Bad',
                            'ErrMsg': 'BadSeqNumber',
                            'ErrId': 3,
                            'SeqNumber': therm.sequence_number,
                            'Sign': sha256(str(therm.sequence_number) + user.plain_password + str(
                                therm.sequence_number)).hexdigest(),
                        }
                        json_response.update(json_response_temp)
                    else:
                        # align and increment the sequence number
                        therm.sequence_number = sequence_number + 1

                        if sha256(str(sequence_number) + user.plain_password + str(
                                sequence_number)).hexdigest() != sign:
                            # Case 4: Sign field not correct
                            json_response_temp = {
                                'Response': 'Bad',
                                'ErrMsg': 'BadSign',
                                'ErrId': 4,
                            }
                            json_response.update(json_response_temp)

                        elif request_type == 'std':
                            # Case 5: history storing of thermostat values
                            history = Historicals()
                            history.temperature = current_state_temp
                            history.mode = current_state_mode

                            therm.history.append(history)

                            therm.put()

                            json_response_temp = {
                                'Response': 'ok',
                                'RemoteSet': 'False',
                                'CurSettings': {
                                    'Hyst': therm.hysteresis,
                                    'TargetTemp': therm.temperature,
                                    'ColdDelay': therm.cold_delay,
                                },
                                'SeqNumber': therm.sequence_number,
                                'Sign': sha256(str(therm.sequence_number) + user.plain_password + str(
                                    therm.sequence_number)).hexdigest(),
                            }
                            json_response.update(json_response_temp)

                        elif request_type == 'set':
                            # Case 6: history storing of thermostat values and update of thermostat current settings
                            history = Historicals()
                            history.temperature = current_state_temp
                            history.mode = current_state_mode
                            therm.history.append(history)

                            therm.temperature = settings_target_temp
                            therm.hysteresis = settings_hysteresis
                            therm.cold_delay = settings_cold_delay

                            therm.put()

                            json_response_temp = {
                                'Response': 'ok',
                                'RemoteSet': 'True',
                                'CurSettings': {
                                    'Hyst': therm.hysteresis,
                                    'TargetTemp': therm.temperature,
                                    'ColdDelay': therm.cold_delay,
                                },
                                'SeqNumber': therm.sequence_number,
                                'Sign': sha256(str(therm.sequence_number) + user.plain_password + str(
                                    therm.sequence_number)).hexdigest(),
                            }
                            json_response.update(json_response_temp)

                        else:
                            json_response_temp = {
                                'Response': 'VeryVeryBad',
                                'ErrMsg': 'UnknownError',
                                'ErrId': -1,
                            }
                            json_response.update(json_response_temp)
        except Exception:
            json_response_temp = {
                'Response': 'Bad',
                'ErrMsg': 'BadRequest',
                'ErrId': 1,
            }
            json_response.update(json_response_temp)

        self.json_response(status_code=200, **json_response)

    def post(self):
        data = self.request.body
        # data = urllib2.unquote(data).decode('utf8') no more needed
        data = json.loads(data)
        # key = 'ahFkZXZ-dGhlcm1vc3Rob3VzZXIYCxILVGhlcm1vc3RhdHMYgICAgIDg1wsM'
        # therm = Thermostats.get_owner_by_key(ndb.Key(urlsafe=key)).get()
        # print therm.owner
        json_response = {}
        try:
            therm_id = int(data['DevId'])
            sequence_number = int(data['SeqNumber'])
            request_type = data['RequestType']
            sign = data['Sign']
            settings_target_temp = float(data['Settings']['TargetTemp'])
            settings_hysteresis = float(data['Settings']['Hyst'])
            settings_cold_delay = int(data['Settings']['ColdDelay'])
            current_state_temp = float(data['CurState']['Temp'])
            current_state_mode = str(data['CurState']['Mode'])
            if therm_id is not None:
                # get the owner information from thermostat indicated by therm_id
                therm = Thermostats.get_by_id(therm_id)
                if therm is None:
                    # case 2: bad device id
                    json_response_temp = {
                        'Response': 'Bad',
                        'ErrMsg': 'BadDevId',
                        'ErrId': 2,
                    }
                    json_response.update(json_response_temp)
                else:
                    # get the information about owner. Password is needed
                    user = Users.get_by_id(therm.owner.id())

                    if sequence_number <= therm.sequence_number:
                        # Case 3: Bad sequence number
                        therm.sequence_number += 1
                        json_response_temp = {
                            'Response': 'Bad',
                            'ErrMsg': 'BadSeqNumber',
                            'ErrId': 3,
                            'SeqNumber': therm.sequence_number,
                            'Sign': sha256(str(therm.sequence_number) + user.plain_password + str(
                                therm.sequence_number)).hexdigest(),
                        }
                        json_response.update(json_response_temp)
                    else:
                        # align and increment the sequence number
                        therm.sequence_number = sequence_number + 1

                        if sha256(str(sequence_number) + user.plain_password + str(
                                sequence_number)).hexdigest() != sign:
                            # Case 4: Sign field not correct
                            json_response_temp = {
                                'Response': 'Bad',
                                'ErrMsg': 'BadSign',
                                'ErrId': 4,
                            }
                            json_response.update(json_response_temp)

                        elif request_type == 'std':
                            # Case 5: history storing of thermostat values
                            history = Historicals()
                            history.temperature = current_state_temp
                            history.mode = current_state_mode

                            therm.history.append(history)

                            therm.put()

                            json_response_temp = {
                                'Response': 'ok',
                                'RemoteSet': 'False',
                                'CurSettings': {
                                    'Hyst': therm.hysteresis,
                                    'TargetTemp': therm.temperature,
                                    'ColdDelay': therm.cold_delay,
                                },
                                'SeqNumber': therm.sequence_number,
                                'Sign': sha256(str(therm.sequence_number) + user.plain_password + str(
                                    therm.sequence_number)).hexdigest(),
                            }
                            json_response.update(json_response_temp)

                        elif request_type == 'set':
                            # Case 6: history storing of thermostat values and update of thermostat current settings
                            history = Historicals()
                            history.temperature = current_state_temp
                            history.mode = current_state_mode
                            therm.history.append(history)

                            therm.temperature = settings_target_temp
                            therm.hysteresis = settings_hysteresis
                            therm.cold_delay = settings_cold_delay

                            therm.put()

                            json_response_temp = {
                                'Response': 'ok',
                                'RemoteSet': 'True',
                                'CurSettings': {
                                    'Hyst': therm.hysteresis,
                                    'TargetTemp': therm.temperature,
                                    'ColdDelay': therm.cold_delay,
                                },
                                'SeqNumber': therm.sequence_number,
                                'Sign': sha256(str(therm.sequence_number) + user.plain_password + str(
                                    therm.sequence_number)).hexdigest(),
                            }
                            json_response.update(json_response_temp)

                        else:
                            json_response_temp = {
                                'Response': 'VeryVeryBad',
                                'ErrMsg': 'UnknownError',
                                'ErrId': -1,
                            }
                            json_response.update(json_response_temp)
        except Exception:
            json_response_temp = {
                'Response': 'Bad',
                'ErrMsg': 'BadRequest',
                'ErrId': 1,
            }
            json_response.update(json_response_temp)

        self.json_response(status_code=200, **json_response)
