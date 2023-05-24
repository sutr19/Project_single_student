#!/bin/bash

echo "Working on updates..."
chmod +x opp.py
./opp.py
sleep 5
ansible-playbook update.yaml