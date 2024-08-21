Project_Single_Student:

bash setup_alises.sh 

 setup_aliases: 
 Writes a block of code into the .bash_aliases file in the user’s home directory. This file will contain:

    install Function: Runs the install.sh script from the specified directory with three arguments.
    operate Function: Runs the operate.sh script from the specified directory with three arguments.
    cleanup Function: Runs the cleanup.sh script from the specified directory with three arguments.

The script overwrites .bash_aliases with these functions, making them available as shell commands.
