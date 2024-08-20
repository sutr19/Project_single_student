import openstack
import sys
from collections import OrderedDict
import deploy as dp
import pprint

tag = "kim-"
#tag = sys.argv[1]+'-'
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

