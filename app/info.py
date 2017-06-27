#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
File for the information page
"""

from framework.request_handler import ThermostHouseRequestHandler


class Info(ThermostHouseRequestHandler):
    def get(self):
        # render an info page of the project
        self.render("info/information.html")
