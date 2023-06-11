#!/bin/bash
opernrc="$1"
tag="$2"
key="$3"
source $opernrc
chmod +x ./all/deploy.py
./all/deploy.py
sleep 5
rm  ~/.ssh/known_hosts
ansible-playbook ./all/deploy.yaml


