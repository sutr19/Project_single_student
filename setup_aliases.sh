#!/bin/bash

# Define the paths
BASH_ALIASES="$HOME/.bash_aliases"
BASHRC="$HOME/.bashrc"
SCRIPT_DIR="/home/roopsai/Desktop/deploy_and_operate_service"

# Create or overwrite the .bash_aliases file with the necessary aliases
echo "Creating or updating $BASH_ALIASES"
cat <<EOL > "$BASH_ALIASES"
# ~/.bash_aliases

# Function to install
install() {
  if [ \$# -ne 3 ]; then
    echo "Usage: install <OpenStack credentials> <revision> <keypair name>"
    return 1
  fi

  # Replace with the actual path to your install.sh script
  bash "$SCRIPT_DIR/install.sh" "\$1" "\$2" "\$3"
}

# Function to operate
operate() {
  if [ \$# -ne 3 ]; then
    echo "Usage: operate <OpenStack credentials> <revision> <keypair name>"
    return 1
  fi

  # Replace with the actual path to your operate.sh script
  bash "$SCRIPT_DIR/operate.sh" "\$1" "\$2" "\$3"
}

# Function to cleanup
cleanup() {
  if [ \$# -ne 3 ]; then
    echo "Usage: cleanup <OpenStack credentials> <revision> <keypair name>"
    return 1
  fi

  # Replace with the actual path to your cleanup.sh script
  bash "$SCRIPT_DIR/cleanup.sh" "\$1" "\$2" "\$3"
}
EOL

# Update the .bashrc file to source .bash_aliases
echo "Updating $BASHRC to source $BASH_ALIASES"
if grep -q 'source ~/.bash_aliases' "$BASHRC"; then
  echo ".bashrc already sources .bash_aliases"
else
  echo 'if [ -f ~/.bash_aliases ]; then' >> "$BASHRC"
  echo '    . ~/.bash_aliases' >> "$BASHRC"
  echo 'fi' >> "$BASHRC"
fi

# Source the updated .bashrc to apply changes
# Use the absolute path to avoid issues with sourcing
source "$HOME/.bashrc"

echo "Setup complete. The .bash_aliases file has been created and .bashrc has been updated."
