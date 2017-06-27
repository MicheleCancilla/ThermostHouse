#!/usr/bin/env python
# -*- coding:utf-8 -*-

from framework.request_handler import ThermostHouseRequestHandler
from models.users import Users


class LoginUser(ThermostHouseRequestHandler):
    def get(self):
        self.render('login/login.html')

    def post(self):
        email = self.request.get('email')
        password = self.request.get('password')

        user_id = Users.check_password(email, password)

        if user_id:
            self.send_cookie(name='User', value=user_id)
            self.redirect('/home')
        else:
            self.redirect('/home')
