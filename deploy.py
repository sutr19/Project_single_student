#!/usr/bin/env python3
import os
#variables
key='p-key'
net='p-network'
subpool='p-pool'
sub='p-subnet'
router='p-router'
port='p-port'
secgroup='p-security'
proxy='p-tag-HAproxy'
bastion='p-tag-bastion'
node='p-tag-node'
fl='1C-1GB-20GB'

#key 
os.system('openstack keypair list>nodes')
with open("nodes") as f:
    if key not in f.read():
        cmd='openstack keypair create {}> private-key'.format(key)
        os.system(cmd)
        os.system('chmod 600 private-key')

#Network
os.system('openstack network list>nodes')
with open("nodes") as f:
    if net not in f.read():
        cmd='openstack network create --tag p-tag {} -f json'.format(net)
        os.system(cmd)
#subnet pool
os.system('openstack subnet pool list>nodes')
with open("nodes") as f:
    if subpool not in f.read():
        cmd='openstack subnet pool create --pool-prefix 10.0.1.0/24 --tag p-tag {} '.format(subpool)
        os.system(cmd)

#subnet
os.system('openstack subnet list>nodes')
with open("nodes") as f:
    if sub not in f.read():
        cmd='openstack subnet create --subnet-pool {} --prefix-length 27 --dhcp --gateway 10.0.1.1 --ip-version 4 --network {} --tag p-tag {} '.format(subpool,net,sub)
        os.system(cmd)

#router
os.system('openstack router list>nodes')
with open("nodes") as f:
    if router not in f.read():
        cmd='openstack router create --tag p-tag {} '.format(router)
        os.system(cmd)


#router add properties
cmd='openstack router add subnet {} {}'.format(router,sub)
os.system(cmd)
cmd1='openstack router set --external-gateway ext-net {}'.format(router)
os.system(cmd1)

#security group
#os.system('openstack security group list>nodes')
#with open("nodes") as f:
 #   if secgroup not in f.read():
  #      cmd='openstack security group create --tag p-tag {}'.format(secgroup)
  #      os.system(cmd)
#rule
#os.system('openstack security group rule create --remote-ip 0.0.0.0/0 --dst-port 22 --protocol tcp --ingress p-security')
#os.system('openstack security group rule create --remote-ip 0.0.0.0/0 --dst-port 80 --protocol tcp --ingress p-security')
#os.system('openstack security group rule create --remote-ip 0.0.0.0/0 --dst-port 5000 --protocol tcp --ingress p-security')
#os.system('openstack security group rule create --remote-ip 0.0.0.0/0 --dst-port 6000 --protocol udp --ingress p-security')
#os.system('openstack security group rule create --remote-ip 0.0.0.0/0 --dst-port 53 --protocol udp --ingress p-security')
#os.system('openstack security group rule create --remote-ip 0.0.0.0/0 --dst-port 80 --protocol icmp --ingress p-security')

#nodes
os.system('openstack server list>nodes')
with open("nodes") as f:
    if proxy not in f.read():
        cmd='openstack server create --image "Ubuntu 22.04.1 Jammy Jellyfish 230124" --flavor {} --key-name {} --network {}  {}'.format(fl,key,net,proxy)
        os.system(cmd)
with open("nodes") as f:
    if bastion not in f.read():
        cmd1='openstack server create --image "Ubuntu 22.04.1 Jammy Jellyfish 230124" --flavor {} --key-name {} --network {}  {}'.format(fl,key,net,bastion)
        os.system(cmd1)

k=1
while k<=3:
    os.system('openstack server list>nodes')
    with open("nodes") as f:
        nod=node+str(k)
        if nod not in f.read():
            cmd2='openstack server create --image "Ubuntu 22.04.1 Jammy Jellyfish 230124" --flavor {} --key-name {} --network {}  {}'.format(fl,key,net,nod)
            os.system(cmd2)
    k+=1
#floating ip
os.system("openstack floating ip create ext-net -f json | jq -r '.floating_ip_address' > floating_ip")
with open("floating_ip") as f:
    fip1=f.read()
os.system("openstack floating ip create ext-net -f json | jq -r '.floating_ip_address' > floating_ip1")
with open("floating_ip1") as f:
    fip2=f.read()


#adding floating ip
c='openstack server add floating ip {} {}'.format(proxy,fip1)
os.system(c)
cc='openstack server add floating ip {} {}'.format(bastion,fip2)
os.system(cc)