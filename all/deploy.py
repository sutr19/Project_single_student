#!/usr/bin/env python3
import os
import re
import subprocess
# variables
key = 'p-key'
net = 'p-network'
subpool = 'p-pool'
sub = 'p-subnet'
router = 'p-router'
port = 'p-port'
secgroup = 'p-security'
proxy1 = 'p-tag-proxy1'
proxy2 = 'p-tag-proxy2'
bastion = 'p-tag-bastion'
node = 'p-tag-node'
fl = '1C-1GB-20GB'


GROUP_HAPROXY = "[Proxy]"
GROUP_WEBSERVERS = "[webservers]"
GROUP_ALL_VARS = "[all:vars]"
BASTION_HOST = "[Bastion]"
Web_Varr = "[webservers:vars]"
node_ips = []

print("Deploying Network..........\n\n")
# key
os.system('openstack keypair list>./all/nodes')
with open("./all/nodes") as f:
    if key not in f.read():
        cmd = 'openstack keypair create {}> ./all/private-key'.format(key)
        os.system(cmd)
        os.system('chmod 600 ./all/private-key')

# Network
os.system('openstack network list>./all/nodes')
with open("./all/nodes") as f:
    if net not in f.read():
        cmd = 'openstack network create --tag p-tag {} -f json'.format(net)
        os.system(cmd)
# subnet pool
os.system('openstack subnet pool list>./all/nodes')
with open("./all/nodes") as f:
    if subpool not in f.read():
        cmd = 'openstack subnet pool create --pool-prefix 10.0.1.0/24 --tag p-tag {} '.format(
            subpool)
        os.system(cmd)

# subnet
os.system('openstack subnet list>./all/nodes')
with open("./all/nodes") as f:
    if sub not in f.read():
        cmd = 'openstack subnet create --subnet-pool {} --prefix-length 27 --dhcp --gateway 10.0.1.1 --ip-version 4 --network {} --tag p-tag {} '.format(
            subpool, net, sub)
        os.system(cmd)

# router
os.system('openstack router list>./all/nodes')
with open("./all/nodes") as f:
    if router not in f.read():
        cmd = 'openstack router create --tag p-tag {} '.format(router)
        os.system(cmd)


# router add properties
cmd = 'openstack router add subnet {} {}'.format(router, sub)
os.system(cmd)
cmd1 = 'openstack router set --external-gateway ext-net {}'.format(router)
os.system(cmd1)

# Nodes
os.system('openstack server list>./all/nodes')
with open("./all/nodes") as f:
    if proxy1 not in f.read():
        cmd = 'openstack server create --image "Ubuntu 22.04.1 Jammy Jellyfish 230124" --flavor {} --key-name {} --network {}  {}'.format(
            fl, key, net, proxy1)
        os.system(cmd)
    if proxy2 not in f.read():
        cmd = 'openstack server create --image "Ubuntu 22.04.1 Jammy Jellyfish 230124" --flavor {} --key-name {} --network {}  {}'.format(
            fl, key, net, proxy2)
        os.system(cmd)
with open("./all/nodes") as f:
    if bastion not in f.read():
        cmd1 = 'openstack server create --image "Ubuntu 22.04.1 Jammy Jellyfish 230124" --flavor {} --key-name {} --network {}  {}'.format(
            fl, key, net, bastion)
        os.system(cmd1)

k = 1
while k <= 3:
    os.system('openstack server list>./all/nodes')
    with open("./all/nodes") as f:
        nod = node+str(k)
        if nod not in f.read():
            cmd2 = 'openstack server create --image "Ubuntu 22.04.1 Jammy Jellyfish 230124" --flavor {} --key-name {} --network {}  {}'.format(
                fl, key, net, nod)
            os.system(cmd2)
    k += 1
# floating ip
os.system("openstack floating ip create ext-net -f json | jq -r '.floating_ip_address' > ./all/floating_ip")
with open("./all/floating_ip") as f:
    fip1 = f.read()
os.system("openstack floating ip create ext-net -f json | jq -r '.floating_ip_address' > ./all/floating_ip1")
with open("./all/floating_ip1") as f:
    fip2 = f.read()


# adding floating ip
c = 'openstack server add floating ip {} {}'.format(proxy1, fip1)
os.system(c)
cc = 'openstack server add floating ip {} {}'.format(bastion, fip2)
os.system(cc)

print("Creating inventory file. Please wait patiently!\n")
if os.path.exists("./all/hosts"):
    os.remove("./all/hosts")
else:
    pass
with open("./all/hosts", 'a+') as f:
    # Add bastion server to hosts file
    bastion_ip = subprocess.check_output("openstack server list | grep 'p-tag-bastion' | cut -d'|' -f5 | cut -d'=' -f2 | cut -d',' -f2", shell=True).decode('utf-8').strip()
   
    bss = f"p-tag-bastion ansible_host={bastion_ip}"
    f.write(f"{BASTION_HOST}\n{bss}\n")
    f.write("\n")
    with open("./all/ssh_config", 'a+') as s:
        s.write(f"{'Host bastion'}\n{'  HostName '}{bastion_ip}\n{'  User ubuntu'}\n{'  IdentityFile ./all/private-key'}\n{'  StrictHostKeyChecking no'}\n")
    # Add HAproxy server to hosts file
    haproxy_ip = subprocess.check_output("openstack server list | grep 'p-tag-proxy1' | cut -d'|' -f5 | cut -d'=' -f2 | cut -d',' -f1", shell=True).decode('utf-8').strip()
    haproxy = f"p-tag-proxy1 ansible_host={haproxy_ip}"
    haproxy_ip1 = subprocess.check_output("openstack server list | grep 'p-tag-proxy2' | cut -d'|' -f5 | cut -d'=' -f2 | cut -d',' -f1", shell=True).decode('utf-8').strip()
    haproxy1 = f"p-tag-proxy2 ansible_host={haproxy_ip1}"
    pub_ip = subprocess.check_output("openstack server list | grep 'p-tag-proxy1' | cut -d'|' -f5 | cut -d',' -f2", shell=True).decode('utf-8').strip()
    f.write(f"{'Public'}\n{'p-tag-proxy3 ansible_host='}{pub_ip}\n")
    f.write("\n")
    f.write(f"{GROUP_HAPROXY}\n{haproxy}\n{haproxy1}\n")
    f.write("\n")
    with open("./all/ssh_config", 'a+') as s:
        s.write(f"{'Host '}{haproxy_ip}\n{'  HostName '}{haproxy_ip}\n{'  User ubuntu'}\n{'  ProxyJump bastion'}\n{'  IdentityFile ./all/private-key'}\n{'  StrictHostKeyChecking no'}\n")
        s.write(f"{'Host '}{haproxy_ip1}\n{'  HostName '}{haproxy_ip1}\n{'  User ubuntu'}\n{'  ProxyJump bastion'}\n{'  IdentityFile ./all/private-key'}\n{'  StrictHostKeyChecking no'}\n")
    # Add web servers to hosts file
    web_servers = subprocess.check_output(
        "openstack server list | grep 'p-tag-node' | cut -d'|' -f5 | cut -d'=' -f2", shell=True).decode('utf-8').strip().split('\n')
    f.write(f"{GROUP_WEBSERVERS}\n")
    for server in web_servers:
        node_ip = subprocess.check_output(
            f"openstack server list | grep {server} | cut -d'|' -f3", shell=True).decode('utf-8').strip()
        node_ips.append(node_ip)
    node_ips.sort()
    with open("./all/ssh_config", 'a+') as s:
        for node_ip in node_ips:
            for server in web_servers:
                if subprocess.check_output(f"openstack server list | grep {server} | cut -d'|' -f3", shell=True).decode('utf-8').strip() == node_ip:
                    node = f"{node_ip} ansible_host={server}"
                    if node not in f.read():
                         f.write(f"{node}\n")
                         s.write(f"{'Host '}{server}\n{'  HostName '}{server}\n{'  User ubuntu'}\n{'  ProxyJump bastion'}\n{'  IdentityFile ./all/private-key'}\n{'  StrictHostKeyChecking no'}\n")

                    else:
                        pass
        f.write("\n")
    f.write(f"{GROUP_ALL_VARS}\n{'ansible_user=ubuntu'}\n")
