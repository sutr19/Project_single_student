#!/bin/bash

wkdir=`dirname $0 | xargs readlink -f`

cd $wkdir
ansible-playbook deploy.yaml
  
