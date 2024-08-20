#!/bin/bash
opernrc="$1"
tag="$2"
key="$3"
unset OS_AUTH_URL
unset OS_USERNAME
unset OS_PASSWORD
source $opernrc
echo "Working on updates..."
chmod +x ./all/cleanup.py.py
./all/cleanup.py $tag $key
sleep 15
ansible-playbook ./all/update.yaml
