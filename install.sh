#!/bin/bash

chmod +x deploy.py
./deploy.py
sleep 5
ansible-playbook deploy.yaml


