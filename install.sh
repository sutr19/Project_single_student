#!/bin/bash
opernrc="$1"
tag="$2"
key="$3"

#!/bin/bash


key="id_rsa"  # Replace with the desired private key name

script_dir="$(dirname "$(realpath "$0")")"

ssh_public_key="$key.pub"
if [ -f "$script_dir/$ssh_public_key" ]; then
  echo "SSH public key '$ssh_public_key' already exists in the script directory."
else

  ssh-keygen -y -f "$script_dir/$key" > "$script_dir/$ssh_public_key"

  if [ $? -ne 0 ]; then
    echo "Error generating SSH public key."
    exit 1
  fi

  echo "SSH public key '$ssh_public_key' created in the script directory."
fi

if [ ! -f "$HOME/.ssh/$ssh_public_key" ]; then
  cp "$script_dir/$ssh_public_key" "$HOME/.ssh/"
  if [ $? -ne 0 ]; then
    echo "Error copying SSH public key to ~/.ssh directory."
    exit 1
  fi
  echo "SSH public key '$ssh_public_key' copied to ~/.ssh directory."
else
  echo "SSH public key '$ssh_public_key' already exists in the ~/.ssh directory."
fi

#!/bin/bash

# Define the paths
KNOWN_HOSTS="$HOME/.ssh/known_hosts"
KNOWN_HOSTS_OLD="$HOME/.ssh/known_hosts.old"

# Check if known_hosts exists
if [ -f "$KNOWN_HOSTS" ]; then
  # Move known_hosts to known_hosts.old
  echo "Moving $KNOWN_HOSTS to $KNOWN_HOSTS_OLD"
  mv "$KNOWN_HOSTS" "$KNOWN_HOSTS_OLD"
else
  # Create known_hosts.old if it doesn't exist
  if [ ! -f "$KNOWN_HOSTS_OLD" ]; then
    echo "Creating $KNOWN_HOSTS_OLD"
    touch "$KNOWN_HOSTS_OLD"
  fi
fi

# Create a new empty known_hosts file
echo "Creating a new empty $KNOWN_HOSTS"
touch "$KNOWN_HOSTS"

echo "Operation complete. $KNOWN_HOSTS has been cleared, and its contents have been moved to $KNOWN_HOSTS_OLD."


unset OS_AUTH_URL
unset OS_USERNAME
unset OS_PASSWORD
source $opernrc
chmod +x ./all/deploy.py
./all/deploy.py $tag $key
#ansible-playbook ./all/deploy.yaml


