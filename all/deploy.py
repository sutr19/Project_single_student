import os
import openstack
import subprocess
import sys
import json
from subprocess import run, CalledProcessError
import pprint

class OpenStackManager:

    def __init__(self, conn, existing_attr, existing_nodes):
        self.conn = conn
        self.attr = existing_attr
        self.nodes = existing_nodes

    def create_keypair(self, key_name: str):
        """
        Generates a 4096-bit RSA key pair without a passphrase and stores them in ~/.ssh/key_name
        """
        key_path = os.path.join("~/.ssh", key_name)
        command = f"ssh-keygen -t rsa -b 4096 -f {key_path} -N "" > {key_path}.pub"

        try:
            run(command, shell=True, check=True)
            print(f"Key pair created: {key_name}")
            
            # Optionally, extract the public key content for use with OpenStack
            with open(f"{key_path}.pub", "r") as f:
                public_key = f.read().strip()
            
            # Call OpenStack keypair create with the extracted public_key
            openstack_command = f"openstack keypair create --public-key {public_key} {key_name}"
            run(openstack_command, shell=True, check=True)
            print(f"OpenStack key pair created: {key_name}")
            
        except CalledProcessError as e:
            print(f"An error occurred while creating key pair: {e}")

    def create_network(self, network_name: str):
        try:
            newnet = self.conn.network.create_network(name=network_name)
            print(f"Network created: {newnet.name}")
            self.update_file('networks', newnet.name)
        except Exception as e:
            print(f"An error occurred while creating network: {e}")


    def create_subnet(self, subnet_name: str, network_name: str): 
        try:
            if network_name in self.existing_attr.get('networks', []):
                new_subnet = self.conn.network.create_subnet(
                    name=subnet_name, cidr="10.0.1.0/26", ip_version=4
            )
                print(f"Subnet created: {new_subnet.name}")
                self.update_file('subnets', new_subnet.name)  
            else:
                print(f"Network {network_name} not found in existing attributes")
        except Exception as e:
            print(f"An error occurred while creating subnet: {e}")

    def create_router(self, router_name: str):
        try:
            existing_routers = [rt.name for rt in self.conn.network.routers()]
            if router_name not in existing_routers:
                new_router = self.conn.network.create_router(name=router_name)
                print(f"Router created: {new_router.name}")
                self.update_file('routers', new_router.name)

                subnet_name = self.existing_attr.get('subnet')
                if subnet_name:
                    new_subnet = self.conn.network.find_subnet(subnet_name)
                    if new_subnet:
                        self.conn.network.add_interface_to_router(new_router.id, subnet_id=new_subnet.id)

                external_network = self.conn.network.find_network("ext-net")
                if external_network:
                    self.conn.network.update_router(new_router.id, external_gateway_info={"network_id": external_network.id})
                else:
                    print("External network not found")
            else:
                print(f"Router {router_name} already exists")
        except Exception as e:
            print(f"An error occurred while creating router: {e}")

    def create_security_group(self, security_group_name: str):
        try:
            new_security = self.conn.network.create_security_group(name=security_group_name)
            rules = [
                {'port_range_min': 22, 'port_range_max': 22},
                {'port_range_min': 80, 'port_range_max': 80},
                {'port_range_min': 53, 'port_range_max': 53},
                {'port_range_min': 5000, 'port_range_max': 5000},
                {'port_range_min': 6000, 'port_range_max': 6000}
            ]
            for rule in rules:
                self.conn.network.create_security_group_rule(
                    security_group_id=new_security.id,
                    direction='ingress',
                    ethertype='IPv4',
                    protocol='tcp',
                    **rule
                )
            self.conn.network.create_security_group_rule(
                security_group_id=new_security.id,
                direction='ingress',
                ethertype='IPv4',
                protocol='icmp'
            )
            print(f"Security group created: {new_security.name}")
            self.update_file('security_groups', new_security.name)
        except Exception as e:
            print(f"An error occurred while creating security group: {e}")

    def create_floating_ip(self):
        command = "openstack floating ip create ext-net -f json"
        try:
            output = subprocess.check_output(command, shell=True).decode('utf-8')
            floating_ip = json.loads(output)['floating_ip_address']
            print(f"Floating IP created: {floating_ip}")
            return floating_ip
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while creating floating IP: {e}")
            return None

    def add_floating_ip_to_server(self, server_id: str, floating_ip: str):
        if server_id and floating_ip:
            command = f"openstack server add floating ip {server_id} {floating_ip}"
            try:
                subprocess.check_output(command, shell=True)
                print(f"Floating IP {floating_ip} added to server {server_id}")
            except subprocess.CalledProcessError as e:
                print(f"An error occurred while adding floating IP to server: {e}")

    def add_security_group(self, server_id: str, security_group: str):
        if server_id and security_group:
            command = f"openstack server add security group {server_id} {security_group}"
            try:
                subprocess.check_output(command, shell=True)
                print(f"Security group {security_group} added to server                          {server_id}")
            except subprocess.CalledProcessError as e:
                print(f"An error occurred while adding security group to server: {e}")

    def create_server(self, server_name: str, image_id: str, flavor_id: str, key_name: str, network_id: str, existing_attr: dict):
        try:
            server = self.conn.compute.create_server(
                name=server_name,
                image_id=image_id,
                flavor_id=flavor_id,
                key_name=key_name,
                networks=[{"uuid": network_id}]
            )
            print(f"Server created: {server_name}")

            # Check for existing floating IP in existing_attr
            floating_ip = existing_attr.get('floating_ip', None) #11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

            # Add floating IP to bastion server
            if server_name == sys.argv[1]+ '-' +'bastion':
                if floating_ip:
                    # Use existing floating IP
                    print(f"Using existing floating IP: {floating_ip}")
                    self.add_floating_ip_to_server(server.id, floating_ip)
                else:
                    # Create and assign new floating IP
                    new_floating_ip = self.create_floating_ip()
                    if new_floating_ip:
                        self.add_floating_ip_to_server(server.id, new_floating_ip)
                        # Update existing_attr with the new floating IP (optional)
                        existing_attr['floating_ip'] = new_floating_ip

            return server
        except Exception as e:
            print(f"An error occurred while creating server {server_name}: {e}")
            return None
    


    def update_file(self, resource_type: str, resource_name: str):
        # Placeholder for updating a file with the resource information
        print(f"Updating {resource_type} file with: {resource_name}")


conn = openstack.connect()

#
#existing_attr = {
#    'keypairs': [keypair.name for keypair in conn.compute.keypairs()],
#    'network': [netw.name for netw in conn.network.find_network()],
#    'router': [rt.name for rt in conn.network.routers()],
#    'security_group': [sg.name for sg in conn.network.security_groups()],
#    'images': [conn.compute.find_image(attr['image'])],
#    'flavor' : [ conn.compute.find_flavor(attr['flavor'])]
#    }

tag = 'mut' + '-'
#tag = sys.argv[1] + '-'

image = subprocess.check_output(
    'openstack image list | grep "Ubuntu" | awk \'{print $2}\' | head -n 1',
    shell=True
).decode('utf-8').strip()

existing_attr = {
    'key': [keypair.name for keypair in conn.compute.keypairs() if keypair.name == tag + 'key'],
    'network': [netw.name for netw in conn.network.networks() if netw.name == tag + 'network'],
    'router': [rt.name for rt in conn.network.routers() if rt.name == tag + 'router'],
    'security_group': [sg.name for sg in conn.network.security_groups() if sg.name == tag + 'security_group'],
    'image': conn.compute.find_image(image),  # Direct image object
    'flavor': conn.compute.find_flavor('1C-1GB-20GB'),  # Direct flavor object
    'floating_ip' : []
}

servers = conn.compute.servers()
existing_nodes = {
    'proxy': [server.name for server in servers if server.name.startswith(tag + 'proxy')],
    'bastion': [server.name for server in servers if server.name.startswith(tag + 'bastion')],
    'node': [server.name for server in servers if server.name.startswith(tag + 'node')]
}

def process_items(existing_items):
    should_create = {}

    for key, value in existing_items.items():
        if not value:  # Check if the value is an empty list
            should_create[key] = tag + key

    return should_create

#combined_should_create = {
#    'should_create_attr': process_items(existing_attr),
#    'should_create__nodes': process_items(existing_nodes)
#}

#pprint.pprint(combined_should_create)
combined_should_create ={'should_create__nodes': {'bastion': 'mut-bastion',
                          'node': 'mut-node',
                          'proxy': 'mut-proxy'},
 'should_create_attr': {'floating_ip': 'mut-floating_ip',
                        'key': 'mut-key',
                        'network': 'mut-network',
                        'router': 'mut-router',
                        'security_group': 'mut-security_group'}}


manager = OpenStackManager(conn, existing_attr, existing_nodes)

for resource_type, resources_name in combined_should_create.items():
    for attr_type,  attr_name in resources_name.items():
        method_name = f"create_{attr_type}"
        method = getattr(manager, method_name, None)
        method_name = "create_{}".format(attr_type)
 
        method = method_name
        print(method)
        if method:
            created_value = method(attr_name)
            if created_value:
                if resource_type.endswith('attr'):
                    existing_attr.setdefault(attr_type, []).append(created_value)
                elif resource_type.endswith('nodes'):
                    existing_nodes.setdefault(attr_type, []).append(created_value)
                    print("Resource " + attr_type + " - " + str(created_value) + " created")

        else:
            print("Method for " + resource_type + " not found")




def get_server_info(server_name):
    """Retrieves hostname, public IP, and private IP for a given server."""
    command = f"openstack server show {server_name} --format json"
    output = subprocess.check_output(command, shell=True, text=True)
    server_data = json.loads(output)

    hostname = server_data['name']
    public_ip = server_data['addresses']['ext-net'][0]['addr']
    private_ip = server_data['addresses']['private'][0]['addr']

    return {
        'hostname': hostname,
        'public_ip': public_ip,
        'private_ip': private_ip
    }

def create_ansible_inventory(bastion_host, proxy_prefix, node_prefix, private_key_file, inventory_dir="./all"):
    """Creates an Ansible inventory and SSH config based on a dictionary of nodes."""

    # Get server information for bastion, HAproxy, and web servers
    bastion_info = get_server_info(bastion_host)
    haproxy_servers = [f"{proxy_prefix}{i}" for i in range(1, 3)]  # Adjust number of HAproxy servers as needed
    haproxy_info = {server: get_server_info(server) for server in haproxy_servers}
    node_servers = [f"{node_prefix}{i}" for i in range(1, 5)]  # Adjust number of web servers as needed
    node_info = {server: get_server_info(server) for server in node_servers}

    # Combine server information into a single dictionary
    nodes_info = {
        bastion_host: bastion_info,
        **haproxy_info,
        **node_info
    }

    # Create inventory file
    inventory_file = os.path.join(inventory_dir, "hosts")
    os.makedirs(inventory_dir, exist_ok=True)

    with open(inventory_file, "w") as f:
        f.write("[Bastion]\n")
        f.write(f"{bastion_host} ansible_host={nodes_info[bastion_host]['private_ip']}\n\n")

        f.write("[HAproxy]\n")
        for haproxy in haproxy_servers:
            f.write(f"{haproxy} ansible_host={nodes_info[haproxy]['private_ip']}\n")
        f.write("\n")

        f.write("[webservers]\n")
        for node in node_servers:
            f.write(f"{node} ansible_host={nodes_info[node]['private_ip']}\n")
        f.write("\n")

        f.write("[all:vars]\n")
        f.write("ansible_user=ubuntu\n")

    # Create SSH config file
    ssh_config_file = os.path.join(inventory_dir, "ssh_config")


    with open(ssh_config_file, "w") as s:
        # Write bastion host config
        bastion_info = nodes[bastion_host]
        s.write(f"Host bastion\n")
        s.write(f"  HostName {bastion_info['public_ip']}\n")
        s.write(f"  User ubuntu\n")
        s.write(f"  IdentityFile {private_key_file}\n")
        s.write(f"  StrictHostKeyChecking no\n\n")

        # Write other nodes config
        for node, info in nodes.items():
            if node != bastion_host:
                s.write(f"Host {info['private_ip']}\n")
                s.write(f"  HostName {info['private_ip']}\n")
                s.write(f"  User ubuntu\n")
                s.write(f"  ProxyJump bastion\n")
                s.write(f"  IdentityFile {private_key_file}\n")
                s.write(f"  StrictHostKeyChecking no\n\n")

if _name_ == "_main_":
    bastion_host = "p-bastion"
    proxy_prefix = "p-haproxy_"
    node_prefix = "p-node_"
    private_key_file = "/path/to/your/key"

    create_ansible_inventory(bastion_host, proxy_prefix, node_prefix, private_key_file)
