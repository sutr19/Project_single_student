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

tag = sys.argv[1] + '-'

image = subprocess.check_output(
    'openstack image list | grep "Ubuntu" | awk \'{print $2}\' | head -n 1',
    shell=True
).decode('utf-8').strip()

existing_attr = {
'key': [keypair.name for keypair in conn.compute.keypairs() if keypair.name == tag + 'key'],
'network': [netw.name for netw in conn.network.find_network() if netw.name == tag + 'network'],
'router': [rt.name for rt in conn.network.routers() if rt.name == tag + 'router'],
'security_group': [sg.name for sg in conn.network.security_groups() if sg.name == tag + 'security_group'],
'image': [conn.compute.find_image(image)],
'flavor': [conn.compute.find_flavor('1C-1GB-20GB')],
'floating_ip' : [ conn.network.get_ip(tag+'floating_ip')]
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

combined_should_create = {
    'should_create_attr': process_items(existing_attr),
    'should_create__nodes': process_items(existing_nodes)
}


