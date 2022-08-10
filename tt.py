import os
with open('nodes') as n:
    i=1
    noden = "p-tag-node"+str(i)
    if noden not in n.read():
        cmd = "openstack server create --image 'Ubuntu 20.04 Focal Fossa 20210616' --flavor {} --key-name {} --network {}  --security-group {} {}".format(
                            fl, key, net, secgroup, noden)
        os.system(cmd)
cmdip='openstack server list | grep {} | cut -d"|" -f"5" | cut -d"=" -f"2">temp_ip'.format(noden)
os.system(cmdip)
with open("temp_ip") as f:
    ip = f.read()
print(ip)