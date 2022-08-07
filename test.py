import os
# i=1
# node_name='p-tag-node'
# while True:
#    with open('nodes') as n:
#        nd=node_name+str(i)
#        if nd not in n.read():
#            print(nd)
#            break
#        else:
#            i+=1


#cmdip='openstack server list | grep {} | cut -d"|" -f"5" | cut -d"=" -f"2">temp_ip'.format(noden)
          # os.system(cmdip)
          # with open("temp_ip") as f:
          #    ip = str(f.read())
           #host = "Hostname " + ip
          #Host = "      HOST " + noden + "\n"
          # with open('ssh_conf', 'w') as f:
          #    f.write(Host)
          #os.system('cat ssh_temp>>ssh_conf')
          # with open('ssh_conf', 'a') as f:
          #    f.write("\n      ")
          #    f.write(host)
          #    f.write("\n")
          #os.system('cat ssh_conf | sudo tee -a /etc/ssh/ssh_config >> /dev/null')
# removing from file
with open("/etc/ssh/ssh_config", 'r') as b:
                for num, line in enumerate(b, 1):
                    if noden in line:
                        n = num+4
                        cmd = "sudo sed '{},{}d' /etc/ssh/ssh_config>ssh_config".format(
                            num, n)
                        cr = ("sudo rm /etc/ssh/ssh_config")
                        mv = ("sudo mv ssh_config /etc/ssh/")
                        os.system(cmd)
                        os.system(cr)
                        os.system(mv)

exist_node = 0
count = 0
fl = '1C-1GB-20GB'
key = 'p-key'
net = 'p-network'
secgroup = 'p-security'
img = 'Ubuntu 20.04 Focal Fossa 20210616'
node_name="p-tag-node"
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
            i = 1
            os.system('openstack server list | grep "p-tag-node" > nodes')
            while True:
                with open('nodes') as n:
                    noden = node_name+str(i)
                    # hostn=noden
                    if noden not in n.read():
                        cmd = "openstack server create --image 'Ubuntu 20.04 Focal Fossa 20210616' --flavor {} --key-name {} --network {}  --security-group {} {}".format(
                            fl, key, net, secgroup, noden)
                        os.system(cmd)
                        cmdip = 'openstack server list | grep {} | cut -d"|" -f"5" | cut -d"=" -f"2">temp_ip'.format(
                           noden)
                        os.system(cmdip)
                        with open("temp_ip") as f:
                            ip = f.read()
                        with open("hosts", 'r+') as b:
                            ll = b.readlines()
                            ll.insert(6, ip)
                            #ll.insert(7, "\n")
                            b.seek(0)
                            b.writelines(ll)
                        break
                    else:
                        i += 1
            to_add -= 1
