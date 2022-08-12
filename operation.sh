#!/bin/bash

wkdir=`dirname $0 | xargs readlink -f`

cd $wkdir
while true;do
  ansible-playbook files/update.yaml
  sleep 30;
done