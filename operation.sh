#!/bin/bash

echo "Working on updates..."
chmod +x ./all/opp.py
./all/opp.py
sleep 5
ansible-playbook ./all/update.yaml