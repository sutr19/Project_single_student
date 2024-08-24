#!/bin/bash

openrc="$1"
tag="$2"
key="$3"

private_key_dir="$(dirname "$key")"
private_key="$key"
public_key="$private_key.pub"

# check existing ssh_key
if [ -f "$private_key" ]; then
  if [ ! -f "$public_key" ]; then
    ssh-keygen -y -f "$private_key" > "$public_key"
    if [ $? -ne 0 ]; then
      echo "Error generating SSH public key."
      exit 1
    fi
    echo "SSH public key '$public_key' created in the same directory as the private key."
  else
    echo "SSH public key '$public_key' already exists."
  fi
else
  echo "Private key '$private_key' does not exist. Please provide a valid private key."
  exit 1
fi



unset OS_AUTH_URL
unset OS_USERNAME
unset OS_PASSWORD
source $openrc
chmod +x ./all/deploy.py
./all/deploy.py $tag $key
ansible-playbook ./all/deploy.yaml


