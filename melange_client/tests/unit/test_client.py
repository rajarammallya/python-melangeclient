#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
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

import json
import urlparse

import httplib2
import mox

from melange_client import client
from melange_client import tests


class TestAuthorizationClient(tests.BaseTest):

    def test_get_token_doesnt_call_auth_service_when_token_is_given(self):
        url = "http://localhost:5001"
        auth_client = client.AuthorizationClient(url,
                                                 "username",
                                                 "access_key",
                                                 "auth_token")
        self.mock.StubOutWithMock(auth_client, "request")

        self.assertEqual(auth_client.get_token(), "auth_token")

    def test_get_token_calls_auth_service_when_token_is_not_given(self):
        url = "http://localhost:5001"
        auth_client = client.AuthorizationClient(url,
                                                 "username",
                                                 "access_key",
                                                  auth_token=None)

        self.mock.StubOutWithMock(auth_client, "request")
        request_body = json.dumps({
            "passwordCredentials": {
                "username": "username",
                'password': "access_key"},
            })

        response_body = json.dumps({'auth': {'token': {'id': "auth_token"}}})
        res = httplib2.Response(dict(status='200'))
        auth_client.request(urlparse.urljoin(url, "/v2.0/tokens"),
                            "POST",
                            headers=mox.IgnoreArg(),
                            body=request_body).AndReturn((res,
                                                          response_body))

        self.mock.ReplayAll()
        self.assertEqual(auth_client.get_token(), "auth_token")

    def test_raises_error_when_retreiveing_token_fails(self):
        url = "http://localhost:5001"
        auth_client = client.AuthorizationClient(url,
                                                 None,
                                                 "access_key",
                                                 auth_token=None)
        self.mock.StubOutWithMock(auth_client, "request")
        res = httplib2.Response(dict(status='401'))
        response_body = "Failed to get token"
        auth_client.request(urlparse.urljoin(url, "/v2.0/tokens"),
                            "POST",
                            headers=mox.IgnoreArg(),
                            body=mox.IgnoreArg()).AndReturn((res,
                                                             response_body))

        self.mock.ReplayAll()
        expected_error_msg = ("Error occured while retrieving token :"
                              " Failed to get token")
        self.assertRaisesExcMessage(Exception,
                                    expected_error_msg,
                                    auth_client.get_token)
