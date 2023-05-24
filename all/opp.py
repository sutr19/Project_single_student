#!/usr/bin/env python3
import os
import time

node_name = 'p-tag-node'
fl = '1C-1GB-20GB'
key = 'p-key'
net = 'p-network'
secgroup = 'p-security'
img = 'Ubuntu 22.04.1 Jammy Jellyfish 230124'
loop = 0
exist_node = 0
with open("servers.conf") as f:
    required_node = int(f.read())
os.system('openstack server list | grep "p-tag-node" > nodes')
with open("nodes") as f:
    lines = f.readlines()
    for line in lines:
        exist_node += 1
if required_node > exist_node:
    to_add = required_node-exist_node
    while to_add > 0:
        i = 1
        k = 10
        os.system('openstack server list | grep "p-tag-node" > nodes')
        while True:
            with open('nodes') as n:
                noden = node_name+str(i)
                if noden not in n.read():
                    cmd = "openstack server create --image 'Ubuntu 22.04.1 Jammy Jellyfish 230124' --flavor {} --key-name {} --network {}  {}".format(
                        fl, key, net,  noden)
                    os.system(cmd)
                    time.sleep(60/6)
                    cmdip = 'openstack server list | grep {} | cut -d"|" -f"5" | cut -d"=" -f"2">temp_ip'.format(
                        noden)
                    os.system(cmdip)
                    with open("temp_ip") as f:
                        ip = f.read()
                        ip1 = "p-tag-node"+str(i)+" ansible_host="+str(ip)
                    with open("ssh_config", 'a+') as s:
                        s.write(
                            f"{'Host '}{ip}\n{'  HostName '}{ip}\n{'  User ubuntu'}\n{'  ProxyJump bastion'}\n{'  IdentityFile ./private-key'}\n{'  StrictHostKeyChecking no'}\n")
                    with open("hosts", 'r+') as b:
                        ll = b.readlines()
                        ll.insert(k, ip1)
                        b.seek(0)
                        b.writelines(ll)
                        k += 1
                    break
                else:
                    i += 1
        to_add -= 1

elif required_node == exist_node:
    pass
else:
    to_del = exist_node-required_node
    while to_del > 0:
        i = 1
        while True:
            os.system('openstack server list | grep "p-tag-node" > nodes')
            with open('nodes') as n:
                noden = node_name+str(i)
                if noden in n.read():
                    cmd = "openstack server delete {}".format(noden)
                    rmnd = "grep -v {} hosts > temphost && mv temphost hosts".format(
                        noden)
                    os.system(cmd)
                    os.system(rmnd)
                    break
                else:
                    i += 1
        to_del -= 1
