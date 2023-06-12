#!/usr/bin/env python3
import os
import time
import sys
import openstack
import subprocess

conn=openstack.connect()
node_name = sys.argv[1]+"-"+'node'
fl = '1C-1GB-20GB'
key = sys.argv[1]+"-"+'key'
net = sys.argv[1]+"-"+'network'
secgroup = sys.argv[1]+"-"+'securityg'
img = 'Ubuntu 22.04.1 Jammy Jellyfish 230124'
image = conn.compute.find_image(img)
flavor = conn.compute.find_flavor(fl)
loop = 0
exist_node = 0
private_key_file = "./all/" + sys.argv[2]

with open("./all/servers.conf") as f:
    required_node = int(f.read())
os.system('openstack server list | grep {} > ./all/nodes'.format(node_name))
global k
word = '[webservers]'
network = conn.network.find_network(net)
with open('./all/hosts', 'r') as file:
    for line_num, line in enumerate(file, 1):
        if word in line:
            k = line_num
with open("./all/nodes") as f:
    lines = f.readlines()
    for line in lines:
        exist_node += 1
if required_node > exist_node:
    to_add = required_node-exist_node
    print(to_add)
    while to_add > 0:
        i = 1
        kk = k
        os.system('openstack server list | grep {} > ./all/nodes'.format(node_name))
        while True:
            with open('./all/nodes') as n:
                noden = node_name+str(i)
                if noden not in n.read():
                    nods = conn.compute.create_server(
                    name=noden, image_id=image.id, flavor_id=flavor.id, key_name=key, networks=[{"uuid": network.id}])
                    conn.compute.wait_for_server(nods)
                    # Attach a tag to proxy
                    metadata = {"tag": sys.argv[1]}
                    conn.compute.set_server_metadata(nods, **metadata)
                    add_security_group_command = "openstack server add security group {} {}".format(nods.id, secgroup)
                    subprocess.check_output(add_security_group_command, shell=True)
                    cmdip = 'openstack server list | grep {} | cut -d"|" -f"5" | cut -d"=" -f"2">./all/temp_ip'.format(
                        noden)
                    os.system(cmdip)
                    with open("./all/temp_ip") as f:
                        ip = f.read()
                        ip1 = node_name+str(i)+" ansible_host="+str(ip)
                    with open("./all/ssh_config", 'a+') as s:
                        s.write(
                            f"{'Host '}{ip}\n{'  HostName '}{ip}\n{'  User ubuntu'}\n{'  ProxyJump bastion'}\n{'  IdentityFile '}{private_key_file}\n{'  StrictHostKeyChecking no'}\n")
                    with open("./all/hosts", 'r+') as b:
                        ll = b.readlines()
                        ll.insert(kk, ip1)
                        b.seek(0)
                        b.writelines(ll)
                        kk += 1
                    break
                else:
                    i += 1
        to_add -= 1

elif required_node == exist_node:
    pass
else:
    to_del = exist_node-required_node
    i = 1
    while i <= to_del:
        k = 1
        time.sleep(5)
        os.system('openstack server list | grep {} > ./all/nodes'.format(node_name))
        while k<10:
            with open('./all/nodes') as n:
                noden = node_name+str(k)
                if noden in n.read():
                    cmd = "openstack server delete {}".format(noden)
                    rmnd = "grep -v {} ./all/hosts > temphost && mv temphost ./all/hosts".format(
                        noden)
                    os.system(cmd)
                    os.system(rmnd)
                    break
                else:
                    k += 1
        i += 1
    else:
        pass
