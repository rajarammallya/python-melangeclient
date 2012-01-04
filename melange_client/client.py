# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import httplib
import httplib2
import json
import socket
import urllib
import urlparse

from melange_client import exception


class HTTPClient(object):

    def __init__(self, host='localhost', port=8080, use_ssl=False, timeout=60):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.timeout = timeout

    def _get_connection(self):
        if self.use_ssl:
            return httplib.HTTPSConnection(self.host,
                                           self.port,
                                           timeout=self.timeout)
        else:
            return httplib.HTTPConnection(self.host,
                                          self.port,
                                          timeout=self.timeout)

    def do_request(self, method, path, body=None, headers=None, params=None):
        params = params or {}
        headers = headers or {}

        url = path + '?' + urllib.urlencode(params)

        try:
            connection = self._get_connection()
            connection.request(method, url, body, headers)
            response = connection.getresponse()
            if response.status >= 400:
                raise exception.MelangeServiceResponseError(response.read())
            return response
        except (socket.error, IOError) as error:
            raise exception.ClientConnectionError(
                _("Error while communicating with server. "
                  "Got error: %s") % error)


class AuthorizationClient(httplib2.Http):

    def __init__(self, url, username, access_key, auth_token=None):
        super(AuthorizationClient, self).__init__()
        self.url = urlparse.urljoin(url, "/v2.0/tokens")
        self.username = username
        self.access_key = access_key
        self.auth_token = auth_token

    def get_token(self):
        if self.auth_token:
            return self.auth_token
        headers = {'content-type': 'application/json'}
        request_body = json.dumps({"passwordCredentials":
                                       {"username": self.username,
                                        'password': self.access_key}})
        res, body = self.request(self.url, "POST", headers=headers,
                                 body=request_body)
        if int(res.status) >= 400:
            raise Exception(_("Error occured while retrieving token : %s")
                              % body)
        return json.loads(body)['auth']['token']['id']
