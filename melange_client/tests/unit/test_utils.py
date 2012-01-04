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
from melange_client import utils


class TestUtils(tests.BaseTest):

    def test_remove_nones(self):
        self.assertEquals(dict(a=1, c=3),
                         utils.remove_nones(dict(a=1, b=None, c=3)))

        self.assertEquals(dict(),
                         utils.remove_nones(dict(a=None, b=None)))

        self.assertEquals(dict(a=1, b=2, c=3),
                         utils.remove_nones(dict(a=1, b=2, c=3)))

    def test_camelize(self):
        self.assertEquals("AaBbCc", utils.camelize("aa_bb_cc"))
        self.assertEquals("Aa", utils.camelize("aa"))
        self.assertEquals("AaBbCc", utils.camelize("AaBbCc"))
