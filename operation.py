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
            hostn=noden
            cmd = "openstack server create --image 'Ubuntu 20.04 Focal Fossa 20210616' --flavor {} --key-name {} --network {}  --security-group {} {}".format(
                fl, key, net, secgroup, hostn)
            with open("hosts", 'r+') as b:
                ll=b.readlines()
                ll.insert(6,noden)
                ll.insert(7,"\n")
                b.seek(0)
                b.writelines(ll)
            cmdip='openstack server list | grep {} | cut -d"|" -f"5" | cut -d"=" -f"2">temp_ip'.format(noden)
            os.system(cmdip)
            with open("temp_ip") as f:
                ip = str(f.read())
            host = "Hostname " + ip 
            Host = "      HOST " + noden + "\n"
            with open('ssh_conf', 'w') as f:
                f.write(Host)
            os.system('cat ssh_temp>>ssh_conf')
            with open('ssh_conf', 'a') as f:
                f.write("\n      ")
                f.write(host)
                f.write("\n")
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
            rmnd = "grep -v {} hosts > temphost && mv temphost hosts".format(noden)
            os.system(cmd)
            os.system(rmnd)
            with open("/etc/ssh/ssh_config", 'r') as b:
                for num, line in enumerate(b,1):
                    if noden in line:
                        n=num+4
                        cmd="sudo sed '{},{}d' /etc/ssh/ssh_config>ssh_config".format(num,n)
                        cr=("sudo rm /etc/ssh/ssh_config")
                        mv=("sudo mv ssh_config /etc/ssh/")
                        os.system(cmd)
                        os.system(cr)
                        os.system(mv)
            to_del -= 1
            exist_node -= 1
    time.sleep(60/2)
