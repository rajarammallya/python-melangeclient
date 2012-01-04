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

import inspect


class MethodInspector(object):

    def __init__(self, func):
        self._func = func

    def required_args(self):
        return self.args()[0:self.required_args_count()]

    def optional_args(self):
        keys = self.args()[self.required_args_count(): len(self.args())]
        return zip(keys, self.defaults())

    def defaults(self):
        return self.argspec().defaults or ()

    def required_args_count(self):
        return len(self.args()) - len(self.defaults())

    def args(self):
        args = self.argspec().args
        if inspect.ismethod(self._func):
            args.pop(0)
        return args

    def argspec(self):
        return inspect.getargspec(self._func)

    def __str__(self):
        optionals = ["[{0}=<{0}>]".format(k) for k, v in self.optional_args()]
        required = ["{0}=<{0}>".format(arg) for arg in self.required_args()]
        args_str = ' '.join(required + optionals)
        return "%s %s" % (self._func.__name__, args_str)


class ClassInspector(object):

    def __init__(self, obj):
        self.obj = obj

    def methods(self):
        """Gets callable public methods.

        Get all callable methods of an object that don't start with underscore
        returns a dictionary of the form dict(method_name, method)

        """

        def is_public_method(attr):
            return (callable(getattr(self.obj, attr))
                    and not attr.startswith('_'))

        return dict((attr, getattr(self.obj, attr)) for attr in dir(self.obj)
                    if is_public_method(attr))
