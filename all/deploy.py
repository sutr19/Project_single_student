#!/usr/bin/env python3

import os
import openstack
import subprocess
import sys
import json
from subprocess import run
from collections import OrderedDict
from pprint import pprint
class OpenStackManager:

    def __init__(self, conn, existing_attr, existing_nodes):
        self.conn = conn
        self.attr = existing_attr
        self.nodes = existing_nodes

    def create_keypair(self, key_name: str):
        pub_key_file = sys.argv[2] + '.pub'
        pub_key_path = os.path.join(os.getcwd(), pub_key_file)
        if not os.path.isfile(pub_key_path):
            print(f"Error: Public key file {pub_key_path} does not exist.")
            return
        openstack_command = f"openstack keypair create --public-key {pub_key_path} {key_name}"
        try:
            subprocess.run(openstack_command, shell=True, check=True)
            print(f"OpenStack key pair created: {key_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error creating key pair: {e}")
    
    def create_network(self, network_name: str):
        newnet = self.conn.network.create_network(name=network_name)
        print(f"Network created: {newnet.name}")
        subnet_name = tag + 'subnet'
        new_subnet = self.conn.network.create_subnet(
            network_id=newnet.id, name=subnet_name, cidr="10.0.1.0/26", ip_version=4
        )
        print(f"Subnet created: {new_subnet.name}")
        
    def create_router(self, router_name: str):
        new_router = self.conn.network.create_router(name=router_name)
        print(f"Router created: {new_router.name}")
        subnet_name = tag +'subnet'
        if subnet_name:
            new_subnet = self.conn.network.find_subnet(subnet_name)
            if new_subnet:
                self.conn.network.add_interface_to_router(new_router.id, subnet_id=new_subnet.id)

        external_network = self.conn.network.find_network("ext-net")
        if external_network:
            self.conn.network.update_router(new_router, external_gateway_info={"network_id": external_network.id})
        else:
            print("External network not found")


    def create_security_group(self, security_group_name: str):
   
        new_security = self.conn.network.create_security_group(name=security_group_name)
    
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
        print(f"Security group created: {new_security.name}")
         

    def create_server(self, server_name: str):
        pprint(self.nodes)  

        image = self.attr.get('image')
        flavor1 =self.attr.get('flavor')
        keypair = self.attr.get('keypair')
        network1 = self.attr.get('network')
        network2= network1[0]

        image = conn.compute.find_image(image)
        flavor = conn.compute.find_flavor(flavor1)
        network = conn.network.find_network(network2)
        key_name=keypair[0]

        if not image or not flavor or not keypair or not network:
            raise ValueError("Missing required attributes in existing_attr")

        server = self.conn.compute.create_server(
                name=server_name,
                image_id=image.id,
                flavor_id=flavor.id,
                key_name=key_name,  # Assuming keypair is a list with one element
                networks=[{"uuid": network.id}]
            )
        
        print(f"Server created: {server_name}")
        security1 = self.attr.get('security_group')
        security = security1[0]
        security_group = conn.network.find_security_group(security)  # Find by name
        if security_group:
            command = f"openstack server add security group {server.id} {security_group.id}"
            try:
                subprocess.check_output(command, shell = True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to add security group: {e.output.decode('utf-8')}")  # Print error message

        floating_ip = subprocess.run(
            ["openstack", "floating", "ip", "list", "--status", "DOWN", "-f", "value", "-c", "Floating IP Address"],
        capture_output=True, check=True).stdout.decode('utf-8').strip().splitlines()

        if server_name == tag + 'bastion' or server_name.startswith(tag + 'proxy'):
            if floating_ip:
                floating_ip_addr = floating_ip[0]

                print(f"Using existing floating IP: {floating_ip_addr}")
                command = "openstack server add floating ip {} {}".format(
                    server.id, floating_ip_addr)
                subprocess.check_output(command, shell=True)
                
            else:
                print("No down floating IP addresses found")
                command1 = "openstack floating ip create ext-net -f json"
                output = subprocess.check_output(command1, shell=True).decode('utf-8')
                floating_ip1 = json.loads(output)['floating_ip_address']
                print(f"Floating IP created: {floating_ip1}")

                command = "openstack server add floating ip {} {}".format(
                    server.id, floating_ip1)
                subprocess.check_output(command, shell=True)
                
            return server            
   #         return f"Error creating server {server_name}: {e}"           

conn = openstack.connect()

tag = sys.argv[1]+'-'

# Retrieve the image ID
image_id = subprocess.check_output(
    'openstack image list | grep "Ubuntu" | awk \'{print $2}\' | head -n 1',
    shell=True
).decode('utf-8').strip()

# Fetch the image and flavor objects
image_obj = conn.compute.find_image(image_id)
flavor_obj = conn.compute.find_flavor('1C-1GB-20GB')

existing_attr = OrderedDict([
    ('keypair', [keypair.name for keypair in conn.compute.keypairs() if keypair.name == tag + 'keypair']),
    ('network', [netw.name for netw in conn.network.networks() if netw.name == tag + 'network']),
    ('router', [rt.name for rt in conn.network.routers() if rt.name == tag + 'router']),
    ('security_group', [sg.name for sg in conn.network.security_groups() if sg.name == tag + 'security_group']), 
    ('image', image_obj.name if image_obj else 'Image not found'),
    ('flavor', flavor_obj.name if flavor_obj else 'Flavor not found')
    ])


servers = conn.compute.servers()
existing_nodes = OrderedDict([
    ('bastion', [server.name for server in servers if server.name.startswith(tag + 'bastion')]),
    ('proxy', [server.name for server in servers if server.name.startswith(tag + 'proxy')]),
    ('node', [server.name for server in servers if server.name.startswith(tag + 'node')])
])


def process_items(existing_items):
    should_create = OrderedDict()

    for key, value in existing_items.items():
        if not value:  # Check if the value is an empty list
            should_create[key] = tag + key

    return should_create

def process_items1(existing_items, item_counts):
    should_create = OrderedDict()

    for key, value in existing_items.items():
        if not value:
            count = item_counts.get(key, 1)  # Default to 1 if key not found
            should_create[key] = [f"{tag}{key}"] if count == 1 else [f"{tag}{key}_{i}" for i in range(1, count + 1)]

    return should_create

item_counts = {
    'proxy': 2,
    'bastion': 1,
    'node': 3
}

combined_should_create = OrderedDict([
    ('should_create_attr', process_items(existing_attr)),
    ('should_create_nodes', process_items1(existing_nodes, item_counts))
])
pprint(existing_attr)
pprint(existing_nodes)
print(combined_should_create)



image = existing_attr.get('image')

manager = OpenStackManager(conn, existing_attr, existing_nodes)

# Create attributes
for attr_type, attr_name in combined_should_create['should_create_attr'].items():
    method_name = f"create_{attr_type}"
    print(f"Creating {method_name}")
    method = getattr(manager, method_name, None)

    if callable(method):
        created_value = method(attr_name)
        if created_value:
            print(f" {created_value} created")

        if isinstance(existing_attr[attr_type], list):
            existing_attr[attr_type].append(attr_name)
            print(f"Attribute {attr_type} - {attr_name} created and added to existing_attr")
    else:
        print(f"Method for creating {attr_type} not found")

pprint(existing_attr)  

#create nodes
for attr_type, attr_names in combined_should_create['should_create_nodes'].items():
    for attr_name in attr_names:
        method_name = f"create_server"
        print(f"Creating {attr_name}")
        method = getattr(manager, method_name, None)

        if callable(method):
            created_value = method(attr_name)
            if created_value:
                print(f" {created_value} created")
            if attr_name in existing_nodes:
                if isinstance(existing_nodes[attr_type], list):
                    existing_nodes.setdefault(attr_type, []).append(attr_name)
                    print(f"Attribute {attr_type} - {attr_name} created and added to existing_nodes")
            else:
            # Add the server name even if the key doesn't exist yet
                existing_nodes.setdefault(attr_type, []).append(attr_name)
                print(f"Attribute {attr_type} - {attr_name} created and added to existing_nodes")
        else:
            print(f"Method for creating {attr_type} not found")
pprint(existing_nodes)


def get_server_info(server_name):
    """Retrieves hostname, public IP, and private IP for a given server."""

    try:
        # Get server details using openstack server show
        command = f"openstack server show {server_name} --format json"
        output = subprocess.check_output(command, shell=True, text=True)
        server_data = json.loads(output)
        hostname = server_data['name']

        # Extract public and private IPs using the provided logic
        command1 = f"openstack server list | grep {server_name} | cut -d'|' -f5 | cut -d'=' -f2 | cut -d',' -f2"
        public_ip = subprocess.check_output(command1, shell=True, text=True).strip()
        command2 = f"openstack server list | grep {server_name} | cut -d'|' -f5 | cut -d'=' -f2 | cut -d',' -f1"
        private_ip = subprocess.check_output(command2, shell=True, text=True).strip()

        return {'hostname': hostname, 'public_ip': public_ip, 'private_ip': private_ip}
    except (subprocess.CalledProcessError, KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error retrieving server info for {server_name}: {e}")
        return None
    

def get_server_info(server_name):
    """Retrieves hostname, public IP, and private IP for a given server."""

    try:
        # Get server details using openstack server show
        command = f"openstack server show {server_name} --format json"
        output = subprocess.check_output(command, shell=True, text=True)
        server_data = json.loads(output)
        hostname = server_data['name']

        # Extract public and private IPs using the provided logic
        command1 = f"openstack server list | grep {server_name} | cut -d'|' -f5 | cut -d'=' -f2 | cut -d',' -f2"
        public_ip = subprocess.check_output(command1, shell=True, text=True).strip()
        command2 = f"openstack server list | grep {server_name} | cut -d'|' -f5 | cut -d'=' -f2 | cut -d',' -f1"
        private_ip = subprocess.check_output(command2, shell=True, text=True).strip()

        return {'hostname': hostname, 'public_ip': public_ip, 'private_ip': private_ip}
    except (subprocess.CalledProcessError, KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error retrieving server info for {server_name}: {e}")
        return None

def create_ansible_inventory(existing_nodes, private_key_file, inventory_dir="./all"):
    inventory_file = os.path.join(inventory_dir, "hosts")
    
    if os.path.exists(inventory_dir) and not os.path.isdir(inventory_dir):
        raise ValueError(f"'{inventory_dir}' exists and is not a directory.")
    
    os.makedirs(inventory_dir, exist_ok=True)
    transformed_nodes = {}

    with open(inventory_file, "w") as f:
        for group_name, node_names in existing_nodes.items():
            f.write(f"[{group_name}]\n")
            transformed_nodes[group_name] = []
            for node_name in node_names:
                node_info = get_server_info(node_name)
                if node_info:
                    transformed_nodes[group_name].append(node_info)
                    hostname = node_info['hostname']
                    if group_name == 'Public':
                        f.write(f"{hostname} public_ip={node_info['public_ip']}\n")
                    else:
                        f.write(f"{hostname} ansible_host={node_info['private_ip'] if not node_info['public_ip'] else node_info['public_ip']}\n")
            f.write("\n")

        # Add specific proxy groups
        if 'proxy' in transformed_nodes:
            proxy_nodes = transformed_nodes['proxy']
            f.write("[proxy1]\n")
            for node in proxy_nodes:
                if node['hostname'].endswith("_1"):
                    hostname = node['hostname']
                    f.write(f"{hostname} ansible_host={node['private_ip']}\n")
            f.write("\n")

            f.write("[proxy2]\n")
            for node in proxy_nodes:
                if node['hostname'].endswith("_2"):
                    hostname = node['hostname']
                    f.write(f"{hostname} ansible_host={node['private_ip']}\n")
            f.write("\n")

            f.write("[proxyprivate]\n")
            for node in proxy_nodes:
                hostname = node['hostname']
                f.write(f"{hostname} ansible_host={node['private_ip']}\n")
            f.write("\n")

        f.write("[all:vars]\n")
        f.write("ansible_user=ubuntu\n")

    # Create SSH config file
    ssh_config_file = os.path.join(inventory_dir, "ssh_config")

    with open(ssh_config_file, "w") as s:
        # Check if 'bastion' key exists in transformed_nodes
        if 'bastion' in transformed_nodes and transformed_nodes['bastion']:
            bastion_info = transformed_nodes['bastion'][0]
            s.write(f"Host bastion\n")
            s.write(f"  HostName {bastion_info['public_ip']}\n")
            s.write(f"  User ubuntu\n")
            s.write(f"  IdentityFile ./{private_key_file}\n")
            s.write(f"  StrictHostKeyChecking no\n\n")

        for node_type, nodes in transformed_nodes.items():
            if node_type != 'bastion':
                for node in nodes:
                    s.write(f"Host {node['private_ip']}\n")
                    s.write(f"HostName {node['private_ip']}\n")
                    s.write(f"  User ubuntu\n")
                    s.write(f"  ProxyJump bastion\n")
                    s.write(f"  IdentityFile ./{private_key_file}\n")
                    s.write(f"  StrictHostKeyChecking no\n\n")


if __name__ == "__main__":
    private_key_file = 'id_rsa'

    create_ansible_inventory(existing_nodes, private_key_file)
