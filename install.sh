#!/bin/bash

wkdir=`dirname $0 | xargs readlink -f`
i=1
cd $wkdir
ansible-playbook deploy.yaml
    

  
