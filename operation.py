import os
count=0
exist_node=0
with open("servers.conf") as f:
    required_node=int(f.read())
os.system('openstack server list | grep "p-tag-node" > nodes')
with open("nodes") as f:
    lines= f.readlines()
for line in lines:
    exist_node+=1
