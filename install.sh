#!/bin/bash
opernrc="$1"
tag="$2"
key="$3"
unset OS_AUTH_URL
unset OS_USERNAME
unset OS_PASSWORD
source $opernrc
chmod +x ./all/deploy.py
./all/deploy.py $tag $key
ansible-playbook ./all/deploy.yaml


