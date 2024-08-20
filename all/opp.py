#!/usr/bin/env python3

import openstack
import sys
from collections import OrderedDict
import deploy as dp
import pprint

tag = sys.argv[1]+'-'
conn = openstack.connect()


opp_existing_attr = OrderedDict([
    ('keypair', [keypair.name for keypair in conn.compute.keypairs() if keypair.name == tag + 'keypair']),
    ('network', [netw.name for netw in conn.network.networks() if netw.name == tag + 'network']),
    ('router', [rt.name for rt in conn.network.routers() if rt.name == tag + 'router']),
    ('security_group', [sg.name for sg in conn.network.security_groups() if sg.name == tag + 'security_group']), 
    ])


servers = conn.compute.servers()
opp_existing_nodes = OrderedDict([
    ('bastion', [server.name for server in servers if server.name.startswith(tag + 'bastion')]),
    ('proxy', [server.name for server in servers if server.name.startswith(tag + 'proxy')]),
    ('node', [server.name for server in servers if server.name.startswith(tag + 'node')])
])


def get_required_nodes():
    with open("./all/servers.conf") as f:
        required_node = int(f.read().strip())
    return required_node



def adjust_server_count():
    """Compares existing and required node counts, creates or deletes servers as needed."""

    existing_nodes = [server.name for server in conn.compute.servers() if server.name.startswith(tag + 'node')]
    required_nodes = get_required_nodes()
    

    # Handle node creation
    for i in range(len(existing_nodes), required_nodes):
        server_name = f"{tag}node_{i+1}"
        try:
            manager = dp.OpenStackManager(conn, opp_existing_attr,opp_existing_nodes )  # Pass empty existing_attr
            manager.create_server(server_name)
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