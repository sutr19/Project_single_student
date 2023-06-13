#!/usr/bin/env python3
import sys
import json
import subprocess
import openstack
import os
# variable
key = 'key'
net = 'network'
subnet = 'subnet'
router = 'router'
proxy = 'proxy'
bastion = 'bastion'
security_group = 'security'
node = 'node'
fl = '1C-1GB-20GB'
img = "Ubuntu 22.04.1 Jammy Jellyfish 230124"


GROUP_HAPROXY = "[Proxy]"
GROUP_WEBSERVERS = "[webservers]"
GROUP_ALL_VARS = "[all:vars]"
BASTION_HOST = "[Bastion]"
Web_Varr = "[webservers:vars]"
node_ips = []
print("Deploying Network Please wait patiently!\n")
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
        network_id=newnet.id, name=subnet, cidr="10.0.1.0/26", ip_version=4)
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

# security group
security_group = sys.argv[1] + "-" + security_group
existing_security = conn.network.find_security_group(name_or_id=security_group)

if existing_security is None:
    new_security = conn.network.create_security_group(name=security_group)
    
    conn.network.create_security_group_rule(
        security_group_id=new_security.id,
        direction='ingress',
        ethertype='IPv4',
        protocol='tcp',
        port_range_min=22,
        port_range_max=22
    )

    conn.network.create_security_group_rule(
        security_group_id=new_security.id,
        direction='ingress',
        ethertype='IPv4',
        protocol='tcp',
        port_range_min=80,
        port_range_max=80
    )

    for port in [53, 5000, 6000]:
        conn.network.create_security_group_rule(
            security_group_id=new_security.id,
            direction='ingress',
            ethertype='IPv4',
            protocol='tcp',
            port_range_min=port,
            port_range_max=port
        )

    conn.network.create_security_group_rule(
        security_group_id=new_security.id,
        direction='ingress',
        ethertype='IPv4',
        protocol='icmp'
    )
else:
    existing_security = [existing_security]

# Nodes
command1 = "openstack floating ip create ext-net -f json"
output1 = subprocess.check_output(command1, shell=True).decode('utf-8')
floating_ip1 = json.loads(output1)['floating_ip_address']
command2 = "openstack floating ip create ext-net -f json"
output2 = subprocess.check_output(command2, shell=True).decode('utf-8')
floating_ip2 = json.loads(output2)['floating_ip_address']
image = conn.compute.find_image(img)
flavor = conn.compute.find_flavor(fl)
network = conn.network.find_network(net)
proxy = sys.argv[1] + "-" + proxy
bastion = sys.argv[1]+"-"+bastion
node = sys.argv[1]+"-"+node
# Check if server proxy1 exists
i = 1
while i <= 2:
    prox = proxy + str(i)
    existser = list(conn.compute.servers(name=prox))
    if len(existser) == 0:
        server = conn.compute.create_server(
            name=prox,
            image_id=image.id,
            flavor_id=flavor.id,
            key_name=key_name,
            networks=[{"uuid": network.id}]
            
        )
        conn.compute.wait_for_server(server)
        # Attach a tag to proxy
        
        metadata = {"tag": sys.argv[1]}
        conn.compute.set_server_metadata(server, **metadata)
        command = "openstack server add floating ip {} {}".format(
            server.id, floating_ip1)
        subprocess.check_output(command, shell=True)
        add_security_group_command = "openstack server add security group {} {}".format(server.id, security_group)
        subprocess.check_output(add_security_group_command, shell=True)
    else:
        print("Server '{}' already exists".format(prox))
    i += 1
else:
    pass
# Check if bastion exists
existbastion = list(conn.compute.servers(name=bastion))
if len(existbastion) == 0:
    srvb = conn.compute.create_server(
        name=bastion, image_id=image.id, flavor_id=flavor.id, key_name=key_name, networks=[
            {"uuid": network.id}]
    )
    conn.compute.wait_for_server(srvb)
    # Attach a tag to proxy2
    metadata = {"tag": sys.argv[1]}
    conn.compute.set_server_metadata(srvb, **metadata)
    command = "openstack server add floating ip {} {}".format(
        srvb.id, floating_ip2)
    subprocess.check_output(command, shell=True)
    add_security_group_command = "openstack server add security group {} {}".format(srvb.id, security_group)
    subprocess.check_output(add_security_group_command, shell=True)
else:
    print("Server '{}' already exists".format(bastion))
# creating worker nodes
k = 1
while k <= 3:
    nod = node + str(k)
    existnode = list(conn.compute.servers(name=nod))
    if len(existnode) == 0:
        nods = conn.compute.create_server(
            name=nod, image_id=image.id, flavor_id=flavor.id, key_name=key_name, networks=[{"uuid": network.id}])
        conn.compute.wait_for_server(nods)
        # Attach a tag to proxy
        metadata = {"tag": sys.argv[1]}
        conn.compute.set_server_metadata(nods, **metadata)
        add_security_group_command = "openstack server add security group {} {}".format(nods.id, security_group)
        subprocess.check_output(add_security_group_command, shell=True)
    else:
        print("Server '{}' already exists".format(nod))
    k += 1
else:
    pass
print("Creating inventory file. Please wait patiently!\n")
if os.path.exists("./all/hosts"):
    os.remove("./all/hosts")
else:
    pass
with open("./all/hosts", 'a+') as f:
    # Add bastion server to hosts file
    command = "openstack server list | grep {} | cut -d'|' -f5 | cut -d'=' -f2 | cut -d',' -f2".format(
        bastion)
    bastion_ip = subprocess.check_output(
        command, shell=True).decode('utf-8').strip()

    bss = f"{bastion} ansible_host={bastion_ip}"
    f.write(f"{BASTION_HOST}\n{bss}\n")
    f.write("\n")
    with open("./all/ssh_config", 'a+') as s:
        s.write(f"{'Host bastion'}\n{'  HostName '}{bastion_ip}\n{'  User ubuntu'}\n{'  IdentityFile '}{private_key_file}\n{'  StrictHostKeyChecking no'}\n")
# Add HAproxy server to hosts file
    hap = proxy + str(1)
    happ = proxy + str(2)
    command4 = "openstack server list | grep {} | cut -d'|' -f5 | cut -d'=' -f2 | cut -d',' -f2".format(
        happ)
    pub_ip = subprocess.check_output(
        command4, shell=True).decode('utf-8').strip()
    command1 = "openstack server list | grep {} | cut -d'|' -f5 | cut -d'=' -f2 | cut -d',' -f1".format(
        hap)
    command2 = "openstack server list | grep {} | cut -d'|' -f5 | cut -d'=' -f2 | cut -d',' -f1".format(
        happ)
    haproxy_ip = subprocess.check_output(
        command1, shell=True).decode('utf-8').strip()
    haproxy = f"{hap} ansible_host={haproxy_ip}"
    haproxy_ip1 = subprocess.check_output(
        command2, shell=True).decode('utf-8').strip()
    haproxy1 = f"{happ} ansible_host={haproxy_ip1}"
    f.write(f"[Public]\ntag-proxy3 public_ip={pub_ip}\n\n")
    f.write(f"{GROUP_HAPROXY}\n{haproxy}\n{haproxy1}\n\n")
    f.write(f"[Proxy1]\n{haproxy}\n\n")
    f.write(f"[Proxy2]\n{haproxy1}\n\n")

    with open("./all/ssh_config", 'a+') as s:
        s.write(f"Host {haproxy_ip}\n  HostName {haproxy_ip}\n  User ubuntu\n  ProxyJump bastion\n  IdentityFile {private_key_file}\n  StrictHostKeyChecking no\n")
        s.write(f"Host {haproxy_ip1}\n  HostName {haproxy_ip1}\n  User ubuntu\n  ProxyJump bastion\n  IdentityFile {private_key_file}\n  StrictHostKeyChecking no\n")
   # Add web servers to hosts file
    command3 = "openstack server list | grep {} | cut -d'|' -f5 | cut -d'=' -f2".format(
        node)
    web_servers = subprocess.check_output(
        command3, shell=True).decode('utf-8').strip().split('\n')
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
                        s.write(
                            f"{'Host '}{server}\n{'  HostName '}{server}\n{'  User ubuntu'}\n{'  ProxyJump bastion'}\n{'  IdentityFile '}{private_key_file}\n{'  StrictHostKeyChecking no'}\n")

                    else:
                        pass
        f.write("\n")
    f.write(f"{GROUP_ALL_VARS}\n{'ansible_user=ubuntu'}\n")
