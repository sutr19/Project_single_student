#!/bin/bash
key='p-key'
net='p-network'
router='p-router'
sub='p-subnet'
subpool='p-pool'
port='p-port'
port1='p-port1'
port2='p-port2'
proxy='p-tag-HAproxy'
bastion='p-tag-bastion'
node1='p-tag-node1'
node2='p-tag-node2'
node3='p-tag-node3'
secgroup='p-security'

#delete key
openstack keypair delete $key


#delete floating IP
openstack floating ip delete $(cat floating_ip)
openstack floating ip delete $(cat floating_ip1)
#delete router
openstack router unset --external-gateway --tag p-tag $router
openstack router remove subnet $router $sub
openstack router delete $router

#port delete
openstack port delete $port
openstack port delete $port1
openstack port delete $port2

#deleting nodes
openstack server delete $proxy
openstack server delete $bastion
openstack server delete $node1
openstack server delete $node2
openstack server delete $node3

#delete subnet poop and subnet 
openstack subnet  delete $sub
openstack subnet pool delete $subpool


#delete network
openstack network delete $net

#delete security group
openstack security group delete $secgroup
