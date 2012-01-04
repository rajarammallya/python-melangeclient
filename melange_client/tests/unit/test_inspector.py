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
from melange_client import inspector


class TestMethodInspector(tests.BaseTest):

    def test_method_without_optional_args(self):
        def foo(bar):
            pass

        method = inspector.MethodInspector(foo)

        self.assertEqual(method.required_args(), ['bar'])
        self.assertEqual(method.optional_args(), [])

    def test_method_with_optional_args(self):
        def foo(bar, baz=1):
            pass

        method = inspector.MethodInspector(foo)

        self.assertEqual(method.required_args(), ['bar'])
        self.assertEqual(method.optional_args(), [('baz', 1)])

    def test_instance_method_with_optional_args(self):
        class Foo():
            def bar(self, baz, qux=2):
                pass

        method = inspector.MethodInspector(Foo().bar)

        self.assertEqual(method.required_args(), ['baz'])
        self.assertEqual(method.optional_args(), [('qux', 2)])

    def test_method_without_args(self):
        def foo():
            pass

        method = inspector.MethodInspector(foo)

        self.assertEqual(method.required_args(), [])
        self.assertEqual(method.optional_args(), [])

    def test_instance_method_without_args(self):
        class Foo():
            def bar(self):
                pass

        method = inspector.MethodInspector(Foo().bar)

        self.assertEqual(method.required_args(), [])
        self.assertEqual(method.optional_args(), [])

    def test_method_str(self):
        class Foo():
            def bar(self, baz, qux=None):
                pass

        method = inspector.MethodInspector(Foo().bar)

        self.assertEqual(str(method), "bar baz=<baz> [qux=<qux>]")
