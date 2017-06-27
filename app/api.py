#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
from hashlib import sha256

from framework.request_handler import ThermostHouseRequestHandler
from models.historicals import Historicals
from models.thermostats import Thermostats
from models.users import Users
import datetime
from dateutil.parser import parse as parse_date


class Api(ThermostHouseRequestHandler):
    def get(self):
        return self.render("/api/api.html")


class ThermostatTempRequest(ThermostHouseRequestHandler):
    """
    API that exports a list of temperature in a range of data
    """

    def post(self):
        data = self.request.body
        # data = json.loads(data)

        json_response = {}
        therm_id = None
        api_key = None
        begin_date = None
        end_date = None
        try:
            therm_id = int(self.request.get('DevId'))
            api_key = str(self.request.get('ApiKey'))
            begin_date = self.request.get('BeginDate')
            end_date = self.request.get('EndDate')
        except Exception:
            json_response = {
                'Response': 'Bad',
                'ErrMsg': 'BadRequest',
                'ErrId': 1,
            }
            return self.json_response(status_code=400, **json_response)

        thermostat = Thermostats.get_by_id(therm_id)
        # from app.plot import plot
        # plot(thermostat)
        # return
        if not thermostat:
            json_response = {
                'Response': 'Bad',
                'ErrMsg': 'BadDevId',
                'ErrId': 2,
            }
            return self.json_response(status_code=400, **json_response)

        # get the information about owner (because password is needed)
        user = Users.get_by_id(thermostat.owner.id())

        if user.API_Key is None:
            json_response = {
                'Response': 'Bad',
                'ErrMsg': 'ApiKeyNotGenerated',
                'ErrId': 3,
            }
            return self.json_response(status_code=400, **json_response)

        if user.API_Key != api_key:
            json_response = {
                'Response': 'Bad',
                'ErrMsg': 'BadApiKey',
                'ErrId': 4,
            }
            return self.json_response(status_code=400, **json_response)

        # # retrieve data of thermostat
        # thermostat = ndb.gql(
        #     "SELECT * FROM Thermostats where __key__ = :1", thermostat.key)
        temperatures = []
        begin_date = parse_date(begin_date).date()
        end_date = parse_date(end_date).date()
        if thermostat.history:
            for sample in thermostat.history:

                if sample.timestamp.date() >= begin_date and sample.timestamp.date() <= end_date:
                    temperatures.append(
                        {
                            'DateTime': str(datetime.datetime(sample.timestamp.year, sample.timestamp.month,
                                                              sample.timestamp.day, sample.timestamp.hour,
                                                              sample.timestamp.minute)),
                            'Temp': sample.temperature,
                        }
                    )
        json_response = {
            'Response': 'Ok',
            'Temperatures': temperatures,
        }

        return self.json_response(status_code=200, **json_response)


class ThermostatDeviceRequest(ThermostHouseRequestHandler):
    """
    API that allows the communication among thermostats and server
    """

    def get(self):
        password = 'a'  # 'lamiabellissimapassworddicomunicazione'
        seq_n = 5
        hashed_pwd = sha256(str(seq_n) + password + str(
            seq_n)).hexdigest()
        # string = "{'DevId': '5687539843203072', 'SeqNumber': 1, 'RequestType': 'std','Sign': '" + hashed_pwd + \
        #          "', 'Settings': {'TargetTemp': 9.90, 'Hyst': 0.50, 'ColdDelay': 3},'CurState': {'Temp': 19.50, 'Mode': 'None'}}"
        string = "{'DevId': '5066549580791808', 'SeqNumber':" + str(seq_n) + ", 'RequestType': 'std',\
         'Settings': {'TargetTemp': 29.70, 'Hyst': 0.50, 'ColdDelay': 2}, 'CurState': {'Temp': 19.50, 'Mode': 'None'},\
         'Sign': '" + hashed_pwd + "'}"
        import ast
        data = ast.literal_eval(string)
        return
        json_response = {}

        therm_id = None
        sequence_number = None
        request_type = None
        sign = None
        settings_target_temp = None
        settings_hysteresis = None
        settings_cold_delay = None
        current_state_temp = None
        current_state_mode = None
        try:
            # Remove char characters from ID
            # therm_id_str = re.sub("[^0-9]", "", data['DevId'])

            therm_id = int(data['DevId'])
            sequence_number = int(data['SeqNumber'])
            request_type = str(data['RequestType'])
            sign = str(data['Sign'])
            settings_target_temp = round(float(data['Settings']['TargetTemp']), 1)
            settings_hysteresis = round(float(data['Settings']['Hyst']), 1)
            settings_cold_delay = int(data['Settings']['ColdDelay'])
            current_state_temp = round(float(data['CurState']['Temp']), 1)
            current_state_mode = str(data['CurState']['Mode'])
        except Exception:
            json_response = {
                'Response': 'Bad',
                'ErrMsg': 'BadRequest',
                'ErrId': 1,
            }
            return self.json_response(status_code=400, **json_response)

        # get the thermostat information by therm_id
        therm = Thermostats.get_by_id(int(therm_id))

        print therm
        if not therm:
            # case 2: bad device id
            json_response = {
                'Response': 'Bad',
                'ErrMsg': 'BadDevId',
                'ErrId': 2,
            }
            return self.json_response(status_code=400, **json_response)
        else:
            # # get the information about owner ( beacuse password is needed)
            # user = Users.get_by_id(therm.owner.id())

            if sequence_number <= therm.sequence_number:
                # Case 3: Bad sequence number
                therm.sequence_number += 1
                json_response = {
                    'Response': 'Bad',
                    'ErrMsg': 'BadSeqNumber',
                    'ErrId': 3,
                    'SeqNumber': therm.sequence_number,
                    'Sign': sha256(str(therm.sequence_number) + therm.plain_password + str(
                        therm.sequence_number)).hexdigest(),
                }
                return self.json_response(status_code=400, **json_response)

            # align and increment the sequence number
            therm.sequence_number = sequence_number + 1

            if sha256(str(sequence_number) + therm.plain_password + str(
                    sequence_number)).hexdigest() != sign:
                # Case 4: Sign field not correct
                json_response = {
                    'Response': 'Bad',
                    'ErrMsg': 'BadSign',
                    'ErrId': 4,
                }
                return self.json_response(status_code=400, **json_response)

            history = Historicals()
            history.temperature = current_state_temp
            history.mode = current_state_mode

            if request_type == 'std':
                # Case 5: history storing of thermostat values
                therm.history.append(history)
                therm.put()

                json_response = {
                    'Response': 'Ok',
                    'RemoteSet': 'False',
                    'CurSettings': {
                        'Hyst': therm.hysteresis,
                        'TargetTemp': therm.temperature,
                        'ColdDelay': therm.cold_delay,
                    },
                    'SeqNumber': therm.sequence_number,
                    'Sign': sha256(str(therm.sequence_number) + therm.plain_password + str(
                        therm.sequence_number)).hexdigest(),
                }
                return self.json_response(status_code=200, **json_response)
            elif request_type == 'set':
                # Case 6: history storing of thermostat values and update of thermostat current settings
                therm.history.append(history)

                therm.temperature = settings_target_temp
                therm.hysteresis = settings_hysteresis
                therm.cold_delay = settings_cold_delay

                therm.put()

                json_response = {
                    'Response': 'Ok',
                    'RemoteSet': 'True',
                    'CurSettings': {
                        'Hyst': therm.hysteresis,
                        'TargetTemp': therm.temperature,
                        'ColdDelay': therm.cold_delay,
                    },
                    'SeqNumber': therm.sequence_number,
                    'Sign': sha256(str(therm.sequence_number) + therm.plain_password + str(
                        therm.sequence_number)).hexdigest(),
                }
                return self.json_response(status_code=200, **json_response)

            json_response = {
                'Response': 'VeryVeryBad',
                'ErrMsg': 'UnknownError',
                'ErrId': -1,
            }
            return self.json_response(status_code=400, **json_response)

    def post(self):
        data = self.request.body
        # data = urllib2.unquote(data).decode()
        data = json.loads(data)

        # key = 'ahFkZXZ-dGhlcm1vc3Rob3VzZXIYCxILVGhlcm1vc3RhdHMYgICAgIDg1wsM'
        # therm = Thermostats.get_owner_by_key(ndb.Key(urlsafe=key)).get()
        # print therm.owner

        json_response = {}

        therm_id = None
        sequence_number = None
        request_type = None
        sign = None
        settings_target_temp = None
        settings_hysteresis = None
        settings_cold_delay = None
        current_state_temp = None
        current_state_mode = None
        try:
            # Remove char characters from ID
            # therm_id_str = re.sub("[^0-9]", "", data['DevId'])

            therm_id = int(data['DevId'])
            sequence_number = int(data['SeqNumber'])
            request_type = str(data['RequestType'])
            sign = str(data['Sign'])
            settings_target_temp = round(float(data['Settings']['TargetTemp']), 1)
            settings_hysteresis = round(float(data['Settings']['Hyst']), 1)
            settings_cold_delay = int(data['Settings']['ColdDelay'])
            current_state_temp = float(data['CurState']['Temp'])
            current_state_mode = str(data['CurState']['Mode'])
        except Exception:
            json_response = {
                'Response': 'Bad',
                'ErrMsg': 'BadRequest',
                'ErrId': 1,
            }
            return self.json_response(status_code=400, **json_response)

        # get the thermostat information by therm_id
        therm = Thermostats.get_by_id(int(therm_id))

        print therm
        if not therm:
            # case 2: bad device id
            json_response = {
                'Response': 'Bad',
                'ErrMsg': 'BadDevId',
                'ErrId': 2,
            }
            return self.json_response(status_code=400, **json_response)
        else:
            # # get the information about owner ( beacuse password is needed)
            # user = Users.get_by_id(therm.owner.id())

            if sequence_number <= therm.sequence_number:
                # Case 3: Bad sequence number
                therm.sequence_number += 1
                json_response = {
                    'Response': 'Bad',
                    'ErrMsg': 'BadSeqNumber',
                    'ErrId': 3,
                    'SeqNumber': therm.sequence_number,
                    'Sign': sha256(str(therm.sequence_number) + therm.plain_password + str(
                        therm.sequence_number)).hexdigest(),
                }
                return self.json_response(status_code=400, **json_response)

            # align and increment the sequence number
            therm.sequence_number = sequence_number + 1

            if sha256(str(sequence_number) + therm.plain_password + str(
                    sequence_number)).hexdigest() != sign:
                # Case 4: Sign field not correct
                json_response = {
                    'Response': 'Bad',
                    'ErrMsg': 'BadSign',
                    'ErrId': 4,
                }
                return self.json_response(status_code=400, **json_response)

            history = Historicals()
            history.temperature = current_state_temp
            history.mode = current_state_mode

            if request_type == 'std':
                # Case 5: history storing of thermostat values
                therm.history.append(history)
                therm.put()

                json_response = {
                    'Response': 'Ok',
                    'RemoteSet': 'False',
                    'CurSettings': {
                        'Hyst': round(therm.hysteresis, 1),
                        'TargetTemp': round(therm.temperature, 1),
                        'ColdDelay': therm.cold_delay,
                    },
                    'SeqNumber': therm.sequence_number,
                    'Sign': sha256(str(therm.sequence_number) + therm.plain_password + str(
                        therm.sequence_number)).hexdigest(),
                }
                return self.json_response(status_code=200, **json_response)
            elif request_type == 'set':
                # Case 6: history storing of thermostat values and update of thermostat current settings
                therm.history.append(history)

                therm.temperature = settings_target_temp
                therm.hysteresis = settings_hysteresis
                therm.cold_delay = settings_cold_delay

                therm.put()

                json_response = {
                    'Response': 'Ok',
                    'RemoteSet': 'True',
                    'CurSettings': {
                        'Hyst': round(therm.hysteresis, 1),
                        'TargetTemp': round(therm.temperature, 1),
                        'ColdDelay': therm.cold_delay,
                    },
                    'SeqNumber': therm.sequence_number,
                    'Sign': sha256(str(therm.sequence_number) + therm.plain_password + str(
                        therm.sequence_number)).hexdigest(),
                }
                return self.json_response(status_code=200, **json_response)

            json_response = {
                'Response': 'VeryVeryBad',
                'ErrMsg': 'UnknownError',
                'ErrId': -1,
            }
            return self.json_response(status_code=400, **json_response)
