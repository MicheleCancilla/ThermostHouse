#!/usr/bin/env python
# -*- coding:utf-8 -*-

from framework.request_handler import ThermostHouseRequestHandler
from models.users import Users


class LoginUser(ThermostHouseRequestHandler):
    def get(self):
        # implement cookie (header in responsible)

        # # substitute %s=%s with the ('Logged_in', 'True') couple
        # #self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % ('Logged_in', 'True'))
        #
        # if self.request.cookies.get('Logged_in'):
        #     print "User is logged in"
        # else:
        #     print "User is not logged in"
        self.render('login/login.html')

    def post(self):
        email = self.request.get('email')
        password = self.request.get('password')

        # print Users.check_password(email, password)

        user_id = Users.check_password(email, password)

        if user_id:
            self.send_cookie(name='User', value=user_id)
            self.redirect('/home')
        else:
            self.redirect('/home')
