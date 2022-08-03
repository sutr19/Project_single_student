import os
import time

node_name = 'p-tag-node'
fl = '1C-1GB-20GB'
key = 'p-key'
net = 'p-network'
secgroup = 'p-security'
img = 'Ubuntu 20.04 Focal Fossa 20210616'


while True:
    exist_node = 0
    count = 0
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
            hostn=noden+"\n"
            cmd = "openstack server create --image 'Ubuntu 20.04 Focal Fossa 20210616' --flavor {} --key-name {} --network {}  --security-group {} {}".format(
                fl, key, net, secgroup, hostn)
            with open("hosts", 'r+') as b:
                ll=b.readlines()
                ll.insert(6,noden)
                b.seek(0)
                b.writelines(ll)
            os.system(
                'openstack server list |grep "p-tag-node3" | cut -d"|" -f"5" | cut -d"=" -f"2">temp_ip')
            with open("temp_ip") as f:
                ip = str(f.read())
            host = "Hostname " + ip + "\n"
            Host = "      HOST " + noden + "\n"
            with open('ssh_conf', 'w') as f:
                f.write(Host)
            os.system('cat ssh_temp>>ssh_conf')
            with open('ssh_conf', 'a') as f:
                f.write("\n      ")
                f.write(host)
            os.system('cat ssh_conf | sudo tee -a /etc/ssh/ssh_config >> /dev/null')
            os.system(cmd)
            to_add -= 1
            i += 1
    elif required_node == exist_node:
        pass
    else:
        to_del = exist_node-required_node
        while to_del > 0:
            noden = node_name+str(exist_node)
            cmd = "openstack server delete {}".format(noden)
            os.system(cmd)
            to_del -= 1
            exist_node -= 1
    time.sleep(60/2)
