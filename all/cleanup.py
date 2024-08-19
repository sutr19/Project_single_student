#!/usr/bin/env python3
import os
from sys import argv
import openstack
import subprocess


net = 'network'
subnet1 = 'subnet'
router1 = 'router'
security_group = 'security'
print("Removing all resources.........\n")
# delete key
conn = openstack.connect()
keypairs = conn.compute.keypairs()
for keypair in keypairs:
    conn.compute.delete_keypair(keypair)
else:
    pass
# delete floating IP
floating_ips = conn.network.ips()
for floating_ip in floating_ips:
    conn.network.delete_ip(floating_ip)

#unset external gateway
routers = conn.network.routers()
for router in routers:
    if router.external_gateway_info:
        conn.network.remove_gateway_from_router(router)
        break

# Remove subnet and delete router
router1=argv[2]+"-"+router1
subnet1=argv[2]+"-"+subnet1
os.system("openstack router unset --external-gateway --tag {} {}".format(argv[2], router1))
os.system("openstack router remove subnet {} {}".format(router1, subnet1))
os.system("openstack router delete {}".format(router1))


# deleting nodes
instances = conn.compute.servers()
for instance in instances:
    conn.compute.delete_server(instance.id)

# delete  subnet
ports = conn.network.ports(fixed_ips='subnet={}'.format(subnet1))
for port in ports:
    for fixed_ip in port.fixed_ips:
        if fixed_ip['subnet_id'] == subnet1:
            port.fixed_ips.remove(fixed_ip)
            break
    conn.network.update_port(port)
os.system("openstack subnet  delete {}".format(subnet1))

# delete network
net=argv[2]+"-"+net
os.system("openstack network delete {}".format(net))
# delete security group
security_group=argv[2]+"-"+security_group
os.system("openstack security group delete {}".format(security_group))