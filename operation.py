import os
count = 0
node_name = 'p-tag-node'
fl = '1C-1GB-20GB'
key = 'p-key'
net = 'p-network'
secgroup = 'p-security'
img = 'Ubuntu 20.04 Focal Fossa 20210616'
exist_node = 0
i = 4
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
        noden = node_name+str(i)
        cmd = "openstack server create --image 'Ubuntu 20.04 Focal Fossa 20210616' --flavor {} --key-name {} --network {}  --security-group {} {}".format(
            fl, key, net, secgroup, noden)
        os.system(cmd)
        to_add -= 1
        i += 1
elif required_node == exist_node:
    print("There are already "+str(required_node)+" Nodes")
else:
    to_del=exist_node-required_node
    while to_del > 0:
        noden = node_name+str(exist_node)
        cmd = "openstack server delete {}".format(noden)
        os.system(cmd)
        to_del -= 1
        exist_node -= 1