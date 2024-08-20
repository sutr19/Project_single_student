#!/usr/bin/env python3
import openstack
import sys
from collections import OrderedDict
from pprint import pprint
import subprocess
import os
import json

tag = sys.argv[1] + '-'
conn = openstack.connect()



def create_server(server_name: str):
    
    image = opp_existing_attr.get('image')
    flavor = opp_existing_attr.get('flavor')
    keypair = opp_existing_attr.get('keypair')
    network = opp_existing_attr.get('network')
    network2 = network[0] if network else None

    image_obj = conn.compute.find_image(image)
    flavor_obj = conn.compute.find_flavor(flavor)
    network_obj = conn.network.find_network(network2)
    key_name = keypair[0] if keypair else None

    if not image_obj or not flavor_obj or not key_name or not network_obj:
        raise ValueError("Missing required attributes in existing_attr")

    server = conn.compute.create_server(
        name=server_name,
        image_id=image_obj.id,
        flavor_id=flavor_obj.id,
        key_name=key_name,  # Assuming keypair is a list with one element
        networks=[{"uuid": network_obj.id}]
    )

    print(f"Server created: {server_name}")
    security_group = opp_existing_attr.get('security_group', [None])[0]
    if security_group:
        security_group_obj = conn.network.find_security_group(security_group)
        if security_group_obj:
            command = f"openstack server add security group {server.id} {security_group_obj.id}"
            try:
                subprocess.check_output(command, shell=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to add security group: {e.output.decode('utf-8')}")  # Print error message

    floating_ips = subprocess.run(
        ["openstack", "floating", "ip", "list", "--status", "DOWN", "-f", "value", "-c", "Floating IP Address"],
        capture_output=True, check=True
    ).stdout.decode('utf-8').strip().splitlines()

    if server_name == tag + 'bastion' or server_name.startswith(tag + 'proxy'):
        if floating_ips:
            floating_ip_addr = floating_ips[0]
            print(f"Using existing floating IP: {floating_ip_addr}")
            command = f"openstack server add floating ip {server.id} {floating_ip_addr}"
            subprocess.check_output(command, shell=True)
        else:
            print("No down floating IP addresses found")
            command1 = "openstack floating ip create ext-net -f json"
            output = subprocess.check_output(command1, shell=True).decode('utf-8')
            floating_ip1 = json.loads(output)['floating_ip_address']
            print(f"Floating IP created: {floating_ip1}")
            command = f"openstack server add floating ip {server.id} {floating_ip1}"
            subprocess.check_output(command, shell=True)
                
    return server
    


# Fetch the image and flavor objects
try:
    image_id = subprocess.check_output(
        'openstack image list | grep "Ubuntu" | awk \'{print $2}\' | head -n 1',
        shell=True
    ).decode('utf-8').strip()
except subprocess.CalledProcessError as e:
    print(f"Error fetching image ID: {e}")
    sys.exit(1)

try:
    image_obj = conn.compute.find_image(image_id)
    flavor_obj = conn.compute.find_flavor('1C-1GB-20GB')
except Exception as e:
    print(f"Error fetching image or flavor: {e}")
    sys.exit(1)

opp_existing_attr = OrderedDict([
    ('keypair', [keypair.name for keypair in conn.compute.keypairs() if keypair.name == tag + 'keypair']),
    ('network', [netw.name for netw in conn.network.networks() if netw.name == tag + 'network']),
    ('router', [rt.name for rt in conn.network.routers() if rt.name == tag + 'router']),
    ('security_group', [sg.name for sg in conn.network.security_groups() if sg.name == tag + 'security_group']), 
    ('image', image_obj.name if image_obj else 'Image not found'),
    ('flavor', flavor_obj.name if flavor_obj else 'Flavor not found')
])

print("Existing Attributes:")
pprint(opp_existing_attr)

# Fetch all servers
try:
    all_servers = list(conn.compute.servers())
except Exception as e:
    print(f"Error fetching servers: {e}")
    sys.exit(1)

# Print all server names for debugging
print("All Server Names:")
for server in all_servers:
    print(server.name)

# Filter servers based on the tag
opp_existing_nodes = OrderedDict([
    ('bastion', [server.name for server in all_servers if server.name.startswith(tag + 'bastion')]),
    ('proxy', [server.name for server in all_servers if server.name.startswith(tag + 'proxy')]),
    ('node', [server.name for server in all_servers if server.name.startswith(tag + 'node')])
])

print("Filtered Existing Nodes:")
pprint(opp_existing_nodes)


    
def get_required_nodes():
    """Reads the number of required nodes from a configuration file."""
    with open("./all/servers.conf") as f:
        required_node = int(f.read().strip())
    return required_node

def adjust_server_count():
    existing_nodes = [server.name for server in conn.compute.servers() if server.name.startswith(tag + 'node')]
    required_nodes = get_required_nodes()
    
    # Handle node creation
    for i in range(len(existing_nodes), required_nodes):
        server_name = f"{tag}node_{i+1}"
        try:
            create_server(server_name)

            print(f"Server {server_name} created.")
        except Exception as e:
            print(f"Error creating server {server_name}: {e}")

    # Handle node deletion
    for i in range(required_nodes, len(existing_nodes)):
        instance_name = existing_nodes.pop()
        try:
            instance = conn.compute.find_server(instance_name)
            if instance:
                conn.compute.delete_server(instance.id)
                print(f"Server {instance_name} deleted.")
        except Exception as e:
            print(f"Error deleting server {instance_name}: {e}")

def main():
    adjust_server_count()

if __name__ == "__main__":
    main()

try:
    all_servers = list(conn.compute.servers())
except Exception as e:
    print(f"Error fetching servers: {e}")
    sys.exit(1)

# Print all server names for debugging
print("All Server Names:")
for server in all_servers:
    print(server.name)

# Filter servers based on the tag
new_existing_nodes = OrderedDict([
    ('bastion', [server.name for server in all_servers if server.name.startswith(tag + 'bastion')]),
    ('proxy', [server.name for server in all_servers if server.name.startswith(tag + 'proxy')]),
    ('node', [server.name for server in all_servers if server.name.startswith(tag + 'node')])
])


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
    private_key_file = sys.argv[2]

    create_ansible_inventory(new_existing_nodes, private_key_file)
