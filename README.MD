Project_Single_Student:

Preliminaries:

Python  3.8.10
Ubuntu  20.04 focal

bash setup_alises.sh 

 setup_aliases: 
 Writes a block of code into the .bash_aliases file in the user’s home directory. This file will contain:

    install Function: Runs the install.sh script from the specified directory with three arguments.
    operate Function: Runs the operate.sh script from the specified directory with three arguments.
    cleanup Function: Runs the cleanup.sh script from the specified directory with three arguments.

The script overwrites .bash_aliases with these functions, making them available as shell commands.


USAGE:

bash setup_aliases.sh

Make sure to check the aliasees are set gloabally 

source ~/bashrc

if an ImageMagik-6 error use 

source ~/.zshrc

Install Nodes and dependencies:

install <openrc> <tag> <ssh_key>

Update NOdes and dependencies:

operate <openrc> <tag> <ssh_key>

Delete 

cleanup <openrc> <tag> <ssh_key>

