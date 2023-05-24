#!/bin/bash

chmod +x deploy.py
#./deploy.py
sleep 5
rm  ~/.ssh/known_hosts
ansible-playbook deploy.yaml


