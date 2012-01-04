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

from melange_client import tests
from melange_client.views.helpers import table


class TestTable(tests.BaseTest):

    def test_padded_keys(self):
        data = [{'k1': 'v1', 'k2':'v12345', 'k1234':'v3'},
                {'k2': 'v22', 'k5': 'v11', 'k1234':'v11'},
               ]
        actual_elem_pads = table.padded_keys(data)

        expected_elem_pads = {
            'k1': len('v1'),
            'k2': len('v12345'),
            'k1234': len('k1234'),
            'k5': len('v11'),
            }

        self.assertEqual(expected_elem_pads, actual_elem_pads)

    def test_row_view(self):

        data = {'k1': 2, 'k2': 3, 'k1234': 6, 9: 4}

        row = table.row_view(sorted(data.iteritems()))

        self.assertEqual("9   \tk1\tk1234 \tk2 ", row)
