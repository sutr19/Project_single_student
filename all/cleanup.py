#!/usr/bin/env python3
import os
import sys
from sys import argv
import openstack
import subprocess
import pprint
from collections import OrderedDict

tag = sys.argv[1] + '-'

conn = openstack.connect()

# Initialize existing_attr
keypair_obj = conn.compute.find_keypair(tag + 'keypair')
network_obj = conn.network.find_network(tag + 'network')
router_obj = conn.network.find_router(tag + 'router')
security_group_obj = conn.network.find_security_group(tag + 'security_group')


#del_keypair = keypair_obj.name
#conn.compute.delete_keypair(del_keypair)
#print(f"Keypair {del_keypair} deleted")



floating_ips = conn.network.ips()
for f_ip in floating_ips:
    conn.network.delete_ip(f_ip.id) 
    print(f"Floating IP {f_ip.id} deleted")


servers = conn.compute.servers()

del_existing_nodes = [server for server in servers if server.name.startswith(tag)]
for instance in del_existing_nodes:
    print(instance.id)
    conn.compute.delete_server(instance.id)


routers = conn.network.routers()
for router in routers:
    pm = router.id
    if router.external_gateway_info:
        conn.network.remove_gateway_from_router(pm)
        break
rr = router_obj.id

dsubnet=argv[1]+"-"+'subnet'
os.system("openstack router unset --external-gateway --tag {} {}".format(argv[1], rr))
os.system("openstack router remove subnet {} {}".format(rr, dsubnet))
os.system("openstack router delete {}".format(rr))

ports = conn.network.ports(fixed_ips='subnet={}'.format(dsubnet))
for port in ports:
    for fixed_ip in port.fixed_ips:
        if fixed_ip['subnet_id'] == dsubnet:
            port.fixed_ips.remove(fixed_ip)
            break
    conn.network.update_port(port)
os.system("openstack subnet  delete {}".format(dsubnet))

net = network_obj.id
os.system("openstack network delete {}".format(net))


sec = security_group_obj.id 
os.system("openstack security group delete {}".format(sec))
