#!/bin/bash

#key 
openstack keypair create p_key

#Network
openstack network create --tag p-tag p-network

#subnet pool
openstack subnet pool create --pool-prefix 10.0.1.0/24 --tag p-tag p-pool

#subnet
openstack subnet create --subnet-pool p-pool --prefix-length 27 --dhcp --gateway 10.0.1.1 --ip-version 4 --network p-network --tag p-tag p-subnet
#router
openstack router create --tag p-tag p-router

#port
openstack port create --network p-network --fixed-ip subnet=p-subnet,ip-address=10.0.1.1 --tag p-tag p-port
openstack port create --network p-network --tag p-tag p-port1
openstack port create --network p-network --tag p-tag p-port2
#router add port 
openstack router add port p-router p-port

#security group
openstack security group create --tag p-tag p-security
#rule
openstack security group rule create --remote-ip 0.0.0.0/0 --dst-port 22 --protocol tcp --ingress p-security
openstack security group rule create --remote-ip 0.0.0.0/0 --dst-port 80 --protocol icmp --ingress p-security

#nodes
openstack server create --image 235d9bfb-7a13-4434-9966-cfc0ae033e79 --flavor 1C-1GB-20GB --key-name p_key --network p-network --security-group p-security p-tag_HAproxy
openstack server create --image 235d9bfb-7a13-4434-9966-cfc0ae033e79 --flavor 1C-1GB-20GB --key-name p_key --network p-network --security-group p-security p-tag_bastion
openstack server create --image 235d9bfb-7a13-4434-9966-cfc0ae033e79 --flavor 1C-1GB-20GB --key-name p_key --network p-network --security-group p-security p-tag_node1
openstack server create --image 235d9bfb-7a13-4434-9966-cfc0ae033e79 --flavor 1C-1GB-20GB --key-name p_key --network p-network --security-group p-security p-tag_node2
openstack server create --image 235d9bfb-7a13-4434-9966-cfc0ae033e79 --flavor 1C-1GB-20GB --key-name p_key --network p-network --security-group p-security p-tag_node3

#floating ip
