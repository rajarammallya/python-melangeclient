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

import re
import os
import subprocess

import melange_client


def camelize(string):
    return re.sub(r"(?:^|_)(.)", lambda x: x.group(0)[-1].upper(), string)


def remove_nones(hash):
    return dict((key, value)
               for key, value in hash.iteritems() if value is not None)


def execute(cmd, raise_error=True):
    """Executes a command in a subprocess.
    Returns a tuple of (exitcode, out, err), where out is the string output
    from stdout and err is the string output from stderr when
    executing the command.

    :param cmd: Command string to execute
    :param raise_error: If returncode is not 0 (success), then
                        raise a RuntimeError? Default: True)

    """

    env = os.environ.copy()

    # Make sure that we use the programs in the
    # current source directory's bin/ directory.
    env['PATH'] = melange_client.melange_bin_path() + ':' + env['PATH']
    process = subprocess.Popen(cmd,
                               shell=True,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               env=env)
    (out, err) = process.communicate()
    exitcode = process.returncode
    if process.returncode != 0 and raise_error:
        msg = "Command %(cmd)s did not succeed. Returned an exit "\
              "code of %(exitcode)d."\
              "\n\nSTDOUT: %(out)s"\
              "\n\nSTDERR: %(err)s" % locals()
        raise RuntimeError(msg)
    return {'exitcode': exitcode, 'out': out, 'err': err}
