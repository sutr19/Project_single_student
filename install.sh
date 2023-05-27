#!/bin/bash

chmod +x ./all/deploy.py
./all/deploy.py
sleep 5
rm  ~/.ssh/known_hosts
ansible-playbook ./all/deploy.yaml


