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

from melange_client import ipam_client
from melange_client import tests


class TestFactory(tests.BaseTest):

    def test_factory_gives_client(self):
        factory = ipam_client.Factory("host", "8080")

        self.assertEquals(ipam_client.IpBlockClient, type(factory.ip_block))

    def test_factory_raises_attribute_error_for_non_existent_client(self):
        factory = ipam_client.Factory("host", "8080")

        self.assertRaisesExcMessage(AttributeError,
                                    "Factory has no attribute "
                                    "non_existent_client",
                                     lambda: factory.non_existent_client)
