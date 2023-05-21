#!/usr/bin/env python3
import subprocess
import re

GROUP_HAPROXY = "[HAproxy]"
GROUP_WEBSERVERS = "[webservers]"
GROUP_ALL_VARS = "[all:vars]"
BASTION_HOST= "[Bastion]"
Web_Varr ="[webservers:vars]"
node_ips = []
if subprocess.os.path.exists("hosts"):
    subprocess.os.remove("hosts")
with open("hosts", 'a+') as f:
    # Add web servers to hosts file
    web_servers = subprocess.check_output("openstack server list | grep 'p-tag-node' | cut -d'|' -f5 | cut -d'=' -f2", shell=True).decode('utf-8').strip().split('\n')
    f.write(f"{GROUP_WEBSERVERS}\n")
    for server in web_servers:
        node_ip = subprocess.check_output(f"openstack server list | grep {server} | cut -d'|' -f3", shell=True).decode('utf-8').strip()
        node_ips.append(node_ip)
    node_ips.sort()
    for node_ip in node_ips:
        for server in web_servers:
            if subprocess.check_output(f"openstack server list | grep {server} | cut -d'|' -f3", shell=True).decode('utf-8').strip() == node_ip:
                node = f"{node_ip} ansible_host={server}"
                if node not in f.read():
                    f.write(f"{node}\n")
                else:
                    pass
    f.write("\n")
    # Add HAproxy server to hosts file
    haproxy_ip = subprocess.check_output("openstack server list | grep 'p-tag-HAproxy' | cut -d'|' -f5 | cut -d'=' -f2 | cut -d',' -f1", shell=True).decode('utf-8').strip()
    haproxy = f"p-tag-HAproxy ansible_host={haproxy_ip}"
    f.write(f"{GROUP_HAPROXY}\n{haproxy}\n")
    f.write("\n")
    # Add bastion server to hosts file
    bastion_ip = subprocess.check_output("openstack server list | grep 'p-tag-bastion' | cut -d'|' -f5 | cut -d'=' -f2 | cut -d',' -f2", shell=True).decode('utf-8').strip()
    ssh_cmd = f"ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ProxyCommand=\"ssh -W %h:%p -q ubuntu@{bastion_ip} -i pub-key\"'"
    bss = f"p-tag-bastion ansible_host={bastion_ip}"
    f.write(f"{BASTION_HOST}\n{bss}\n")
    f.write("\n")
    # Add authorized_keys to webservers group vars
    f.write(f"{Web_Varr}\n{'ansible_user=ubuntu'}\n{'ansible_ssh_private_key_file=pub-key'}\n{ssh_cmd}\n")
    f.write("\n")
    f.write(f"{GROUP_ALL_VARS}\n{'ansible_user=ubuntu'}\n")
