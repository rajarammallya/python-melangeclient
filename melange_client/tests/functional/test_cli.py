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
import uuid
import yaml

from melange_client import tests
from melange_client import utils
from melange_client.tests import functional
from melange_client.tests.functional import template_test_helper
from melange_client.tests.functional import factory


class TestBaseCLI(tests.BaseTest, template_test_helper.TemplateTestHelper):

    def setUp(self):
        self.maxDiff = None
        self.tenant_id = str(uuid.uuid4())

    def command(self, command_name, is_tenanted=True, raise_error=True,
                **kwargs):
        parameters = ["%s=%s" % (key, value)
                     for key, value in kwargs.iteritems()]
        cmd_args = " ".join(parameters)
        if is_tenanted:
            return functional.run("{0} -t {1} {2} ".format(command_name,
                                                self.tenant_id,
                                                cmd_args),
                                                raise_error=raise_error)
        else:
            return functional.run("{0} {1} ".format(command_name, cmd_args),
                                  raise_error=raise_error)

    def assertShows(self, res_name, expected_resource, is_tenanted=True,
                    command_name=None, parameters=""):
        command_name = command_name or res_name
        parameters = parameters or "id=%s" % expected_resource['id']
        tenant_option = "-t %s" % self.tenant_id if is_tenanted else ""

        show_command = ("%s show %s %s"
                       % (command_name, parameters, tenant_option))
        show_res = functional.run(show_command)

        shown_resource = factory.model(res_name, show_res)
        for key, expected_resource_field in expected_resource.iteritems():
            self.assertEqual(expected_resource_field, shown_resource[key])

    def assertResourceNotFound(self, res_name, expected_resource,
                               is_tenanted=True, command_name=None,
                               parameters=""):
        command_name = command_name or res_name
        parameters = parameters or "id=%s" % expected_resource['id']
        tenant_option = "-t %s" % self.tenant_id if is_tenanted else ""

        show_res = functional.run("%s show %s %s " % (command_name,
                                                      parameters,
                                                      tenant_option),
                                   raise_error=False)
        self.assertTrue("%s Not Found" % utils.camelize(res_name)
                        in show_res['out'])


class TestIpBlockCLI(TestBaseCLI):

    def test_crud(self):
        create_res = functional.run("ip_block create type=private "
                                    "cidr=10.1.1.0/29 network_id=%s "
                                    "-t %s" % (uuid.uuid4(), self.tenant_id))
        ip_block = factory.model('ip_block', create_res)
        self.assertEqual(0, create_res['exitcode'])
        self.assertShows('ip_block', ip_block)

        update_res = functional.run("ip_block update id=%s network_id=%s "
                                    "-t %s" % (ip_block['id'],
                                               uuid.uuid4(),
                                               self.tenant_id))
        updated_block = factory.model('ip_block', update_res)
        self.assertEqual(0, update_res['exitcode'])
        self.assertShows('ip_block', updated_block)

        deleted_res = functional.run("ip_block delete "
                                     "id=%s -t %s" % (ip_block['id'],
                                                      self.tenant_id))
        self.assertEqual(0, deleted_res['exitcode'])
        self.assertResourceNotFound('ip_block', ip_block)

    def test_list(self):
        block1 = factory.create_block(self.tenant_id)
        block2 = factory.create_block(self.tenant_id)
        list_res = functional.run("ip_block list -t %s" % self.tenant_id)

        self.assertEqual(0, list_res['exitcode'])
        self.assertEqual(sorted([block1, block2]),
                         sorted(factory.model('ip_blocks', list_res)))

    def test_list_without_tenant_id_should_error_out(self):
        self.assertRaises(RuntimeError,
                          functional.run,
                          "ip_block list")


class TestSubnetCLI(TestBaseCLI):

    def test_create_and_list(self):
        block = factory.create_block(cidr="10.0.0.0/8", tenant_id="123")
        subnet_res_1 = functional.run("subnet create parent_id={0} "
                         "cidr=10.0.1.0/29 -t 123".format(block['id']))
        self.assertEqual(0, subnet_res_1['exitcode'])

        subnet_res_2 = functional.run("subnet create parent_id={0} "
                         "cidr=10.0.0.0/29 -t 123".format(block['id']))
        self.assertEqual(0, subnet_res_2['exitcode'])

        subnet_list_res = functional.run("subnet list parent_id={0} "
                              "-t 123".format(block['id']))
        self.assertEqual(sorted([factory.model('subnet', subnet_res_1),
                                 factory.model('subnet', subnet_res_2)]),
                         sorted(factory.model('subnets', subnet_list_res)))


class TestPolicyCLI(TestBaseCLI):

    def test_list(self):
        policy1 = factory.create_policy(self.tenant_id)
        policy2 = factory.create_policy(self.tenant_id)
        list_res = functional.run("policy list -t %s" % self.tenant_id)

        self.assertEqual(sorted([policy1, policy2]),
                         sorted(yaml.load(list_res['out'])['policies']))

    def test_crud(self):
        create_res = self.command("policy create",
                                  name="policy_name",
                                  desc="policy_desc")
        self.assertEqual(0, create_res['exitcode'])
        policy = factory.model('policy', create_res)
        self.assertShows('policy', policy)

        update_res = self.command("policy update",
                                  id=policy['id'],
                                  name="new_name")
        self.assertEqual(0, update_res['exitcode'])
        updated_policy = factory.model('policy', update_res)
        self.assertShows('policy', updated_policy)

        delete_res = self.command("policy delete", id=policy['id'])
        self.assertEqual(0, delete_res['exitcode'])

        self.assertResourceNotFound('policy', policy)


class TestUnusableIpRangesCLI(TestBaseCLI):

    def test_create(self):
        policy = factory.create_policy(tenant_id=self.tenant_id)

        create_res = self.command('unusable_ip_range create',
                                  policy_id=policy['id'],
                                  offset=1,
                                  length=2)

        ip_range = factory.model('ip_range', create_res)
        self.assertShows('ip_range',
                          ip_range,
                          command_name="unusable_ip_range",
                          parameters="id=%s policy_id=%s" % (ip_range['id'],
                                                             policy['id']))
        update_res = self.command('unusable_ip_range update',
                                  policy_id=policy['id'],
                                  id=ip_range['id'],
                                  offset=10,
                                  length=122)
        updated_ip_range = factory.model('ip_range', update_res)
        self.assertShows('ip_range',
                         updated_ip_range,
                         command_name="unusable_ip_range",
                        parameters="id=%s policy_id=%s" % (ip_range['id'],
                                                           policy['id']))

        another_create_res = self.command('unusable_ip_range create',
                                          policy_id=policy['id'],
                                          offset=1,
                                          length=2)

        another_ip_range = factory.model('ip_range', another_create_res)

        list_res = functional.run("unusable_ip_range list"
                       " policy_id={0} -t {1}".format(policy['id'],
                           self.tenant_id))

        self.assertEqual(sorted([updated_ip_range, another_ip_range]),
                         sorted(yaml.load(list_res['out'])['ip_ranges']))

        self.command("unusable_ip_range delete",
                     policy_id=policy['id'],
                     id=ip_range['id'])

        parameters = ("policy_id=%s id=%s" % (policy['id'],
                                              ip_range['id']))
        self.assertResourceNotFound("ip_range",
                                    ip_range,
                                    command_name="unusable_ip_range",
                                    parameters=parameters)


class TestUnusableIpOctetsCLI(TestBaseCLI):

    def test_crud(self):
        policy = factory.create_policy(tenant_id=self.tenant_id)

        create_res = self.command('unusable_ip_octet create',
                                  policy_id=policy['id'],
                                  octet=255)
        ip_octet = factory.model('ip_octet', create_res)
        self.assertShows('ip_octet',
                         ip_octet,
                         command_name="unusable_ip_octet",
                         parameters="id=%s policy_id=%s" % (ip_octet['id'],
                                                            policy['id']))

        update_res = self.command('unusable_ip_octet update',
                                  policy_id=policy['id'],
                                  id=ip_octet['id'],
                                  octet=200)
        updated_ip_octet = factory.model('ip_octet', update_res)
        self.assertShows('ip_octet', updated_ip_octet,
                          command_name="unusable_ip_octet",
                          parameters="id=%s policy_id=%s" % (ip_octet['id'],
                                                             policy['id']))

        another_create_res = self.command('unusable_ip_octet create',
                                          policy_id=policy['id'],
                                          octet=200)
        another_ip_octet = factory.model('ip_octet', another_create_res)

        list_res = functional.run("unusable_ip_octet list policy_id={0}"
                                  " -t {1}".format(policy['id'],
                                                   self.tenant_id))

        self.assertEqual(sorted([updated_ip_octet, another_ip_octet]),
                         sorted(yaml.load(list_res['out'])['ip_octets']))

        self.command("unusable_ip_octet delete",
                     policy_id=policy['id'],
                     id=ip_octet['id'])

        parameters = "policy_id=%s id=%s" % (policy['id'],
                                              ip_octet['id'])
        self.assertResourceNotFound("ip_octet",
                                    ip_octet,
                                    command_name='unusable_ip_octet',
                                    parameters=parameters)


class TestAllocatedIpAddressCLI(TestBaseCLI):

    def test_list(self):
        device1_id, device2_id = uuid.uuid4(), uuid.uuid4()
        block = factory.create_block(cidr="30.1.1.1/24",
                                      tenant_id=self.tenant_id)
        ip1 = factory.create_ip(block_id=block['id'],
                                 address="30.1.1.2",
                                 used_by_device=device1_id,
                                 tenant_id=self.tenant_id)
        ip2 = factory.create_ip(block_id=block['id'],
                                 address="30.1.1.3",
                                 used_by_device=device2_id,
                                 tenant_id=self.tenant_id)

        list_res = self.command("allocated_ip list",
                                 is_tenanted=False,
                                 used_by_device=device1_id)

        self.assertEqual([ip1], yaml.load(list_res['out'])['ip_addresses'])

    def test_list_with_tenant(self):
        device1_id, device2_id = uuid.uuid4(), uuid.uuid4()
        tenant1_id, tenant2_id = uuid.uuid4(), uuid.uuid4()
        block = factory.create_block(cidr="30.1.1.1/24",
                                      tenant_id=self.tenant_id)
        tenant1_ip1 = factory.create_ip(block_id=block['id'],
                                         address="30.1.1.2",
                                         used_by_device=device1_id,
                                         tenant_id=self.tenant_id,
                                         used_by_tenant=tenant1_id,)
        tenant1_ip2 = factory.create_ip(block_id=block['id'],
                                         address="30.1.1.3",
                                         used_by_device=device1_id,
                                         tenant_id=self.tenant_id,
                                         used_by_tenant=tenant1_id,)
        tenant2_ip1 = factory.create_ip(block_id=block['id'],
                                         address="30.1.1.4",
                                         used_by_device=device2_id,
                                         tenant_id=self.tenant_id,
                                         used_by_tenant=tenant2_id)

        list_res = functional.run("allocated_ip list -t %s" % tenant1_id)

        self.assertEqual(sorted([tenant1_ip1, tenant1_ip2]),
                         sorted(yaml.load(list_res['out'])['ip_addresses']))


class TestIpAddressCLI(TestBaseCLI):

    def test_crud(self):
        block = factory.create_block(cidr="10.1.1.0/24",
                                      tenant_id=self.tenant_id)

        ip = factory.create_ip(block_id=block['id'],
                                address="10.1.1.2",
                                tenant_id=self.tenant_id)

        self._assert_ip_shows(ip)

        another_ip = factory.create_ip(block_id=block['id'],
                                        address="10.1.1.3",
                                        tenant_id=self.tenant_id)

        list_res = self.command("ip_address list",
                                ip_block_id=block['id'])

        self.assertEqual(sorted([ip, another_ip]),
                         sorted(yaml.load(list_res['out'])['ip_addresses']))

        self.command("ip_address delete",
                     ip_block_id=block['id'],
                     address="10.1.1.2")

        # TODO: fix bug 911255 on show of deallocated addresses
        # show_res = functional.run("ip_address show ip_block_id=%s address=%s"
        #                "-t %s" % (block['id'], "10.1.1.2", self.tenant_id),
        #                raise_error=False)

        # self.assertTrue("IpAddress Not Found" in show_res['out'])

    def _assert_ip_shows(self, expected_resource):
        show_command = ("ip_address show ip_block_id=%s address=%s "
                       "-t %s" % (expected_resource['ip_block_id'],
                                  expected_resource['address'],
                                  self.tenant_id))
        show_res = functional.run(show_command)
        shown_resource = factory.model('ip_address', show_res)
        for key, expected_resource_field in expected_resource.iteritems():
            self.assertEqual(expected_resource_field, shown_resource[key])


class TestIpRoutesCLI(TestBaseCLI):

    def test_crud(self):
        block = factory.create_block(cidr="77.1.1.0/24",
                                      tenant_id=self.tenant_id)
        create_res = self.command("ip_route create",
                                  ip_block_id=block['id'],
                                  destination="10.1.1.2",
                                  gateway="10.1.1.1",
                                  netmask="255.255.255.0")
        route = factory.model("ip_route", create_res)
        self.assertShows("ip_route",
                          route,
                          parameters="ip_block_id=%s id=%s" % (block['id'],
                                                               route['id']))

        another_create_res = self.command("ip_route create",
                                          ip_block_id=block['id'],
                                          destination="20.1.1.2",
                                          gateway="20.1.1.1",
                                          netmask="255.255.255.0")
        another_route = factory.model("ip_route", another_create_res)

        list_res = self.command("ip_route list",
                                ip_block_id=block['id'])
        self.assertTableEquals([route, another_route], list_res['out'])

        self.command("ip_route delete",
                     ip_block_id=block['id'],
                     id=route['id'])

        self.assertResourceNotFound("ip_route",
                                    route,
                                    parameters="ip_block_id=%s id=%s"
                                    % (block['id'], route['id']))


class TestInterfaceCLI(TestBaseCLI):

    def test_crud(self):
        iface = factory.create_interface(tenant_id=self.tenant_id)
        self.assertShows("interface",
                          iface,
                          parameters="vif_id=%s" % iface['id'])

        self.command("interface delete", is_tenanted=False, vif_id=iface['id'])
        self.assertResourceNotFound("interface",
                                    iface,
                                    parameters="vif_id=%s" % iface['id'])


class TestMacAddressRangeCLI(TestBaseCLI):

    def test_crud(self):
        create_res = self.command("mac_address_range create",
                                  is_tenanted=False,
                                  cidr="ab-bc-cd-12-23-34/2")
        rng = factory.model('mac_address_range', create_res)
        self.assertShows('mac_address_range', rng, is_tenanted=False)
        another_create_res = self.command("mac_address_range create",
                                          is_tenanted=False,
                                          cidr="bc-ab-dc-12-23-34/2")
        another_rng = factory.model('mac_address_range', another_create_res)

        list_res = self.command("mac_address_range list", is_tenanted=False)
        rng_list = yaml.load(list_res['out'])['mac_address_ranges']
        self.assertTrue(rng in rng_list)
        self.assertTrue(another_rng in rng_list)

        self.command("mac_address_range delete",
                     is_tenanted=False,
                     id=rng['id'])
        self.assertResourceNotFound('mac_address_range',
                                    rng,
                                    is_tenanted=False)


class TestAllowedIpCLI(TestBaseCLI):

    def test_crud(self):
        network_id = uuid.uuid4()
        iface = factory.create_interface(network_id=network_id,
                                          tenant_id=self.tenant_id)
        block = factory.create_block(cidr="20.1.1.0/24",
                                      network_id=network_id,
                                      tenant_id=self.tenant_id)
        ip = factory.create_ip(address="20.1.1.2",
                                block_id=block['id'],
                                used_by_tenant=self.tenant_id,
                                tenant_id=self.tenant_id)
        another_ip = factory.create_ip(address="20.1.1.3",
                                        block_id=block['id'],
                                        used_by_tenant=self.tenant_id,
                                        tenant_id=self.tenant_id)

        ip_res = self.command("allowed_ip create",
                              interface_id=iface['id'],
                              network_id=network_id,
                              ip_address=ip['address'])
        allowed_ip = factory.model("ip_address", ip_res)
        self.assertShows("ip_address",
                         allowed_ip,
                         parameters="interface_id=%s ip_address=%s" %
                                    (iface['id'], ip['address']),
                         command_name="allowed_ip")

        another_ip_res = self.command("allowed_ip create",
                                      interface_id=iface['id'],
                                      network_id=network_id,
                                      ip_address=another_ip['address'])

        another_allowed_ip = factory.model('ip_address', another_ip_res)

        list_res = self.command("allowed_ip list", interface_id=iface['id'])
        actual_allowed_ips = yaml.load(list_res['out'])['ip_addresses']
        self.assertTrue(allowed_ip in actual_allowed_ips)
        self.assertTrue(another_allowed_ip in actual_allowed_ips)

        self.command("allowed_ip delete",
                     interface_id=iface['id'],
                     ip_address=ip['address'])
        show_res = self.command("allowed_ip show",
                                interface_id=iface['id'],
                                ip_address=ip['address'],
                                raise_error=False)
        expected_error = ("Ip Address %s hasnt been allowed on interface %s" %
                          (ip['address'], iface['id']))
        self.assertTrue(expected_error in show_res['out'])


class TestMelangeCLI(TestBaseCLI):

    def test_raises_error_for_non_keyword_arguments(self):
        res = functional.run("allowed_ip delete interface_id123 -t RAX",
                             raise_error=False)
        self.assertEqual(res['exitcode'], 2)
        self.assertIn("Action arguments should be of the form of field=value",
                      res['out'])
