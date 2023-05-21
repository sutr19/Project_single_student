#!/bin/bash
filename="~/.ssh/known_hosts"
echo "Deploying Network......"
chmod +x deploy.py
./deploy.py
if test -e "$filename"; then
    rm "$filename"
fi

echo "Configuring hosts....."
ip_add=$(openstack server list | grep 'p-tag-bastion' | cut -d'|' -f5 | cut -d'=' -f2 | cut -d',' -f2 | tr -d ' ')
ssh -o "StrictHostKeyChecking=no" ubuntu@"$ip_add"
ansible-playbook deploy.yaml
