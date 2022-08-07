import os
count=0
cmd='openstack server list | grep "p-tag-HAproxy" | cut -d"|" -f"5" | cut -d"=" -f"2" | cut -d"," -f"1">temp_ip'
os.system(cmd)
with open("temp_ip", 'r') as f:
    ip=f.read()
with open("hosts", 'r+') as f:
    ll=f.readlines()
    if ip not in ll:
        ll.insert(1,ip)
        f.seek(0)
        f.writelines(ll)
cmd1='openstack server list | grep "p-tag-node" | cut -d"|" -f"5" | cut -d"=" -f"2">temp_ip'
os.system(cmd1)
with open("temp_ip", 'r') as f:
    ip1=f.read()
with open("hosts", 'r+') as b:
    for line in b:
        if line in ip1:
            count+=1
if count==0:
    with open("hosts", 'r+') as b:
        l1=b.readlines()
        ll.insert(3,ip1)
        b.seek(0)
        b.writelines(ll)
cmd2='openstack server list | grep "p-tag-bastion" | cut -d"|" -f"5" | cut -d"=" -f"2" | cut -d"," -f"2">temp_ip'
os.system(cmd2)
with open("temp_ip", 'r') as f:
    ip2=f.read()
    ip2=ip2.rstrip('\n')
cmd3="ansible_ssh_common_args="+"\'-o StrictHostKeyChecking=no -o ProxyCommand="+"\"ssh -o \\\'ForwardAgent yes\\\' ubuntu@"+ip2+"-p 2222 \\\'ssh-add pub-key && nc %h %p\\\'\"-p 2222\'"+"\n"
c=0
with open("hosts", 'r+') as b:
    for line in b:
        if cmd3 in line:
            c+=1
if c==0:
    with open("hosts", 'r+') as b:
        l1=b.readlines()
        ll.insert(10,cmd3)
        b.seek(0)
        b.writelines(ll)
