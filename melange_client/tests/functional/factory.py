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

import uuid
import yaml

from melange_client.tests import functional


def create_policy(tenant_id="123"):
    create_res = functional.run("policy create name=policy_name "
                                "desc=policy_desc "
                                "-t %s" % tenant_id)
    return yaml.load(create_res['out'])['policy']


def create_ip(address="10.1.1.1", used_by_tenant=None,
              used_by_device="device", interface_id=None,
              block_id=None, tenant_id=None):
    used_by_tenant = used_by_tenant or tenant_id
    interface_id = interface_id or uuid.uuid4()
    block_id = block_id or create_block(cidr="10.1.1.1/24",
                                        tenant_id=tenant_id)['id']
    create_res = functional.run("ip_address create ip_block_id=%s address=%s "
                "interface_id=%s used_by_tenant=%s "
                "used_by_device=%s -t %s " % (block_id, address, interface_id,
                                             used_by_tenant, used_by_device,
                                             tenant_id))
    return model("ip_address", create_res)


def create_interface(vif_id=None, device_id="device", network_id=None,
        tenant_id=None):
    vif_id = vif_id or uuid.uuid4()

    network_id = network_id or uuid.uuid4()
    tenant_id = tenant_id or uuid.uuid4()
    create_res = functional.run("interface create vif_id=%s tenant_id=%s "
                     "device_id=%s network_id=%s" % (vif_id, tenant_id,
                                                     device_id, network_id))
    return model("interface", create_res)


def create_block(tenant_id="1234", cidr="10.1.1.0/29", network_id=None):
    network_id = network_id or uuid.uuid4()
    create_res = functional.run("ip_block create type=private "
                     "cidr=%(cidr)s network_id=%(network_id)s "
                     "-t %(tenant_id)s" % locals())
    return model('ip_block', create_res)


def model(name, res):
    return yaml.load(res['out'])[name]
