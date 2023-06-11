#!/usr/bin/env python3
import os
from sys import argv
import openstack
import subprocess


net = 'network'
subnet1 = 'subnet'
router1 = 'router'

print("Removing all resources.........\n")
command = ". {}".format(argv[1])  
subprocess.call(command, shell=True)
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

# Iterate over the instances and delete them
for instance in instances:
    conn.compute.delete_server(instance.id)


# delete network
os.system("openstack network delete {}".format(subnet1))

# delete security group
#os.system("openstack security group delete p-security")

def remove_lines(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    with open(filename, 'w') as file:
        file.writelines(lines[:53])  # Keep lines from 1 to 53 (inclusive)

# Usage example
filename = './all/ssh_config'  
remove_lines(filename)