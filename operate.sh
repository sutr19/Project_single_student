#!/bin/bash

echo "Working on updates..."
chmod +x ./all/opp.py
./all/opp.py
sleep 10
ansible-playbook ./all/update.yaml