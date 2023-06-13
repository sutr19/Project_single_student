#!/usr/bin/env python3
import os
from sys import argv
import openstack
import subprocess


net = 'network'
subnet1 = 'subnet'
router1 = 'router'
security_group = 'securityg'
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
port_list_cmd = ["openstack", "port", "list", "--fixed-ip", f"subnet={subnet1}", "--format", "value", "-c", "ID"]
port_ids = subprocess.run(port_list_cmd, capture_output=True, text=True).stdout.strip().split('\n')

# Detach each port from the subnet
for port_id in port_ids:
    detach_cmd = ["openstack", "port", "unset", "--no-security-group", "--subnet", subnet1, port_id]
    subprocess.run(detach_cmd)

os.system("openstack subnet  delete {}".format(subnet1))

# delete network
net=argv[2]+"-"+net
os.system("openstack network delete {}".format(net))

# delete  subnet
os.system("openstack subnet  delete {}".format(subnet1))

# delete security group
security_group=argv[2]+"-"+security_group
os.system("openstack security group delete {}".format(security_group))

#deleting privati key
private_key_file = "./all/" + argv[3]
if os.path.exists(private_key_file):
    os.remove(private_key_file)
else:
    pass

#deleting ssh_config
def remove_lines(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    with open(filename, 'w') as file:
        file.writelines(lines[:53])  

filename = './all/ssh_config'  
remove_lines(filename)