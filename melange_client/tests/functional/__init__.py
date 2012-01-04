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

import ConfigParser
import os

import melange_client
from melange_client import utils


def run(command, **kwargs):
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(melange_client.melange_root_path(),
                             "tests/functional/tests.conf"))
    full_command = "{0} --host={1} --port={2} {3} -v ".format(
                    melange_client.melange_bin_path('melange'),
                    config.get('DEFAULT', 'server_name'),
                    config.get('DEFAULT', 'server_port'),
                    command)
    return utils.execute(full_command, **kwargs)
