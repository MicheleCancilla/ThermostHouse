#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

import httplib2
from google.appengine.api import memcache
from googleapiclient.discovery import build
from oauth2client.contrib.appengine import OAuth2DecoratorFromClientSecrets

CLIENT_SECRETS = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)),
    'conf/client_secrets.json')

MISSING_CLIENT_SECRETS_MESSAGE = """
<h1>Warning: Please configure OAuth 2.0</h1>
<p>
To make this sample run you will need to populate the client_secrets.json file
found at:
</p>
<p>
<code>%s</code>.
</p>
<p>with information found on the <a
href="https://code.google.com/apis/console">APIs Console</a>.
</p>
"""

http = httplib2.Http(memcache)

service = build("plus", "v1", http=http)

decorator = OAuth2DecoratorFromClientSecrets(
    CLIENT_SECRETS,
    scope=['https://www.googleapis.com/auth/plus.login',
           'https://www.googleapis.com/auth/userinfo.email'],
    message=MISSING_CLIENT_SECRETS_MESSAGE)
