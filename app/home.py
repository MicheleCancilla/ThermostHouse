#!/usr/bin/env python
# -*- coding:utf-8 -*-
from framework.request_handler import ThermostHouseRequestHandler


class Home(ThermostHouseRequestHandler):
    def get(self):
        self.render('home/home.html')
