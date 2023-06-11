#!/usr/bin/env python3
import os
from sys import argv
import openstack
import subprocess

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


# unset external gateway
routers = conn.network.routers()
for router in routers:
    if router.external_gateway_info:
        conn.network.remove_gateway_from_router(router)
        break

# Delete routers
for router in routers:
    conn.network.delete_router(router)

# Delete subnets
subnets = conn.network.subnets()
for subnet in subnets:
    conn.network.delete_subnet(subnet)
#os.system("openstack router unset --external-gateway --tag p-tag p-router")
#os.system("openstack router remove subnet p-router p-subnet")
#os.system("openstack router delete p-router")


# deleting nodes
#os.system('openstack server list | grep "p-tag" | cut -d"|" -f"3" >./all/nodes')
#with open("./all/nodes") as f:
#    for line in f:
#        cmd = 'openstack server delete {}'.format(line)
#        os.system(cmd)
#os.system('grep -v "10.0.1" hosts > temphost && mv temphost hosts')   
#os.system('grep -v "ansible_ssh_common_args=" hosts > temphost && mv temphost hosts')

# delete subnet pool and subnet
#os.system("openstack subnet  delete p-subnet")
#os.system("openstack subnet pool delete p-pool")


# delete network
#os.system("openstack network delete p-network")

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