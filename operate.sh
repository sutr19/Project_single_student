#!/bin/bash
opernrc="$1"
tag="$2"
key="$3"
source $opernrc
echo "Working on updates..."
chmod +x ./all/opp.py
./all/opp.py $tag $key
sleep 15
ansible-playbook ./all/update.yaml