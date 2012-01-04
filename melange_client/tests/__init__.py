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

import unittest

import mox


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.mock = mox.Mox()
        super(BaseTest, self).setUp()

    def assertUnorderedEqual(self, expected, actual):
        self.assertEqual(sorted(expected), sorted(actual))

    def assertRaisesExcMessage(self, exception, message,
                               func, *args, **kwargs):
        """This is similar to assertRaisesRegexp in python 2.7"""

        try:
            func(*args, **kwargs)
            self.fail("Expected {0} to raise {1}".format(func,
                                                         repr(exception)))
        except exception as error:
            self.assertIn(message, str(error))
