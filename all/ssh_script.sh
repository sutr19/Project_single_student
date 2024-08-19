#!/bin/bash

# Private key name
ssh_key="id_rsa"

# Public key path
ssh_public_key="$ssh_key.pub"

# Check if the public key already exists in the /all directory
if [ -f "/all/$ssh_public_key" ]; then
  echo "SSH public key '$ssh_public_key' already exists in the /all directory."
else
  # Generate the public key from the private key and store it directly in the /all directory
  ssh-keygen -y -f "./$ssh_key" > "/all/"

  if [ $? -ne 0 ]; then
    echo "Error generating SSH public key."
    exit 1
  fi

  echo "SSH public key '$ssh_public_key' created in the /all directory."
fi

