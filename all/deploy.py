#!/usr/bin/env python3
import sys
# import re
# import subprocess
import openstack
import os
# variables
key = 'key'
net = 'network'
# subpool = 'p-pool'
subnet = 'subnet'
router = 'router'
# secgroup = 'p-security'
proxy = 'proxy'
proxy2 = 'proxy2'
bastion = 'bastion'
# node = 'p-tag-node'
fl = '1C-1GB-20GB'
img = "Ubuntu 22.04.1 Jammy Jellyfish 230124"


# GROUP_HAPROXY = "[Proxy]"
# GROUP_WEBSERVERS = "[webservers]"
# GROUP_ALL_VARS = "[all:vars]"
# BASTION_HOST = "[Bastion]"
# Web_Varr = "[webservers:vars]"
# node_ips = []
conn = openstack.connect()

keyp = [keypair.name for keypair in conn.compute.keypairs()]
key_name = sys.argv[1] + "-" + key
private_key_file = "./all/" + sys.argv[2]

if key_name not in keyp:
    try:
        keypair = conn.compute.create_keypair(name=key_name)
        with open(private_key_file, "w") as f:
            f.write(keypair.private_key)
        os.chmod(private_key_file, 0o600)
    except openstack.exceptions.SDKException as e:
        print("Failed to create key pair:", str(e))
else:
    print("Key pair '{}' already exists".format(key_name))
# Network
netlist = conn.network.networks()
existnet = [netw.name for netw in netlist]
net = sys.argv[1] + "-" + net
subnet = sys.argv[1] + "-" + subnet
router = sys.argv[1] + "-" + router
if net not in existnet:
    newnet = conn.network.create_network(name=net)
    tags = [sys.argv[1]]
    conn.network.set_tags(newnet, tags)
    # create subnet
    new_subnet = conn.network.create_subnet(
        network_id=newnet.id, name=subnet, cidr="10.0.1.0/24", ip_version=4)
    conn.network.set_tags(new_subnet, tags)

    # create router
    routerlist = conn.network.routers()
    existrouter = [rt.name for rt in routerlist]
    if router not in existrouter:
        newrouter = conn.network.create_router(name=router)
        conn.network.set_tags(newrouter, tags)
        # Add subnet to the router
        conn.network.add_interface_to_router(
            newrouter.id, subnet_id=new_subnet.id)
        # Set external network to router
        external_network = conn.network.find_network("ext-net")
        if external_network:
            conn.network.update_router(newrouter, external_gateway_info={"network_id": external_network.id}
                                       )
        else:
            print("External network not found")
    else:
        print("Router '{}' already exists".format(router))
else:
    print("Network '{}' already exists".format(net))


# Nodes
image = conn.compute.find_image(img)
flavor = conn.compute.find_flavor(fl)
network = conn.network.find_network(net)
proxy = sys.argv[1] + "-" + proxy
bastion = sys.argv[1]+"-"+bastion
# Check if server proxy1 exists
i=1
while i<=2:
    prox=proxy+str(i)
    existser = conn.compute.servers(name=prox)
    if prox not in existser:
        server = conn.compute.create_server(
        name=prox, image_id=image.id, flavor_id=flavor.id, key_name=key_name, networks=[{"uuid": network.id}])
        conn.compute.wait_for_server(server)
        # Attach a tag to proxy
        metadata = {"tag": sys.argv[1]}
        conn.compute.set_server_metadata(server, **metadata)  
    else:
       print("Server '{}' already exists".format(proxy))
    i+=1
else:
    pass
# Check if bastion exists
existbastion = conn.compute.servers(name=bastion)
if bastion not in existbastion:
    srvb = conn.compute.create_server(
        name=bastion, image_id=image.id, flavor_id=flavor.id, key_name=key_name, networks=[{"uuid": network.id}])
    conn.compute.wait_for_server(srvb)
    # Attach a tag to proxy2
    metadata = {"tag": sys.argv[1]}
    conn.compute.set_server_metadata(srvb, **metadata)
else:
    print("Server '{}' already exists".format(bastion))

# 
# k = 1
# while k <= 3:
#    os.system('openstack server list>./all/nodes')
#    with open("./all/nodes") as f:
#        nod = node+str(k)
#        if nod not in f.read():
#            cmd2 = 'openstack server create --image "Ubuntu 22.04.1 Jammy Jellyfish 230124" --flavor {} --key-name {} --network {}  {}'.format(
#                fl, key, net, nod)
#            os.system(cmd2)
#    k += 1
# floating ip
# os.system("openstack floating ip create ext-net -f json | jq -r '.floating_ip_address' > ./all/floating_ip")
# with open("./all/floating_ip") as f:
#    fip1 = f.read()
# os.system("openstack floating ip create ext-net -f json | jq -r '.floating_ip_address' > ./all/floating_ip1")
# with open("./all/floating_ip1") as f:
#    fip2 = f.read()


# adding floating ip
# c = 'openstack server add floating ip {} {}'.format(proxy1, fip1)
# os.system(c)
# ccc = 'openstack server add floating ip {} {}'.format(proxy2, fip1)
# os.system(ccc)
# cc = 'openstack server add floating ip {} {}'.format(bastion, fip2)
# os.system(cc)

# print("Creating inventory file. Please wait patiently!\n")
# if os.path.exists("./all/hosts"):
#    os.remove("./all/hosts")
# else:
#    pass
# with open("./all/hosts", 'a+') as f:
#    # Add bastion server to hosts file
#    bastion_ip = subprocess.check_output("openstack server list | grep 'p-tag-bastion' | cut -d'|' -f5 | cut -d'=' -f2 | cut -d',' -f2", shell=True).decode('utf-8').strip()
#
#    bss = f"p-tag-bastion ansible_host={bastion_ip}"
#    f.write(f"{BASTION_HOST}\n{bss}\n")
#    f.write("\n")
#    with open("./all/ssh_config", 'a+') as s:
#        s.write(f"{'Host bastion'}\n{'  HostName '}{bastion_ip}\n{'  User ubuntu'}\n{'  IdentityFile ./all/private-key'}\n{'  StrictHostKeyChecking no'}\n")
# Add HAproxy server to hosts file
#    haproxy_ip = subprocess.check_output("openstack server list | grep 'p-tag-proxy1' | cut -d'|' -f5 | cut -d'=' -f2 | cut -d',' -f1", shell=True).decode('utf-8').strip()
#    haproxy = f"p-tag-proxy1 ansible_host={haproxy_ip}"
#    haproxy_ip1 = subprocess.check_output("openstack server list | grep 'p-tag-proxy2' | cut -d'|' -f5 | cut -d'=' -f2 | cut -d',' -f1", shell=True).decode('utf-8').strip()
#    haproxy1 = f"p-tag-proxy2 ansible_host={haproxy_ip1}"
#   # pub_ip = subprocess.check_output("openstack server list | grep 'p-tag-proxy1' | cut -d'|' -f5 | cut -d',' -f2", shell=True).decode('utf-8').strip()
#    f.write(f"{'Public'}\n{'p-tag-proxy3 public_ip='}{fip1}\n")
#    f.write("\n")
#    f.write(f"{GROUP_HAPROXY}\n{haproxy}\n{haproxy1}\n")
#    f.write("\n")
#    with open("./all/ssh_config", 'a+') as s:
#        s.write(f"{'Host '}{haproxy_ip}\n{'  HostName '}{haproxy_ip}\n{'  User ubuntu'}\n{'  ProxyJump bastion'}\n{'  IdentityFile ./all/private-key'}\n{'  StrictHostKeyChecking no'}\n")
#        s.write(f"{'Host '}{haproxy_ip1}\n{'  HostName '}{haproxy_ip1}\n{'  User ubuntu'}\n{'  ProxyJump bastion'}\n{'  IdentityFile ./all/private-key'}\n{'  StrictHostKeyChecking no'}\n")
#    # Add web servers to hosts file
#    web_servers = subprocess.check_output(
#        "openstack server list | grep 'p-tag-node' | cut -d'|' -f5 | cut -d'=' -f2", shell=True).decode('utf-8').strip().split('\n')
#    f.write(f"{GROUP_WEBSERVERS}\n")
#    for server in web_servers:
#        node_ip = subprocess.check_output(
#            f"openstack server list | grep {server} | cut -d'|' -f3", shell=True).decode('utf-8').strip()
#        node_ips.append(node_ip)
#    node_ips.sort()
#    with open("./all/ssh_config", 'a+') as s:
#        for node_ip in node_ips:
#            for server in web_servers:
#                if subprocess.check_output(f"openstack server list | grep {server} | cut -d'|' -f3", shell=True).decode('utf-8').strip() == node_ip:
#                    node = f"{node_ip} ansible_host={server}"
#                    if node not in f.read():
#                         f.write(f"{node}\n")
#                         s.write(f"{'Host '}{server}\n{'  HostName '}{server}\n{'  User ubuntu'}\n{'  ProxyJump bastion'}\n{'  IdentityFile ./all/private-key'}\n{'  StrictHostKeyChecking no'}\n")#

#                   else:
# pass
#       f.write("\n")
#   f.write(f"{GROUP_ALL_VARS}\n{'ansible_user=ubuntu'}\n")
