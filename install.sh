#!/bin/bash
opernrc="$1"
tag="$2"
key="$3"
source $opernrc
chmod +x ./all/deploy.py
./all/deploy.py $tag $key
ansible-playbook ./all/deploy.yaml


