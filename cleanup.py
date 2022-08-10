#!/usr/bin/env python3
import os
import time

# delete key
os.system("openstack keypair delete p-key")

# delete floating IP
os.system("openstack floating ip delete $(cat floating_ip)")
os.system("openstack floating ip delete $(cat floating_ip1)")

# delete router
os.system("openstack router unset --external-gateway --tag p-tag p-router")
os.system("openstack router remove subnet p-router p-subnet")
os.system("openstack router delete p-router")

# port delete
os.system("openstack port delete p-port")
os.system("openstack port delete p-port1")
os.system("openstack port delete p-port2")

# deleting nodes
os.system('openstack server list | grep "p-tag" | cut -d"|" -f"3" >nodes')
with open("nodes") as f:
    for line in f:
        cmd = 'openstack server delete {}'.format(line)
        os.system(cmd)
os.system('grep -v "10.0.1" hosts > temphost && mv temphost hosts')   
os.system('grep -v "ansible_ssh_common_args=" hosts > temphost && mv temphost hosts')

# delete subnet poop and subnet
os.system("openstack subnet  delete p-subnet")
os.system("openstack subnet pool delete p-pool")


# delete network
os.system("openstack network delete p-network")

# delete security group
os.system("openstack security group delete p-security")
