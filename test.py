import os
#noden = 'p-tag-node1'
#Host = "      HOST " + noden + "\n"
#with open('ssh_conf', 'w') as f:
#    f.write(Host)
#os.system('cat ssh_temp>>ssh_conf')
#with open("temp_ip") as f:
 #   ip = str(f.read())
#host = "Hostname " + ip + "\n" 
#with open('ssh_conf', 'a') as f:
 #   f.write("\n      ")
 #   f.write(host)
#os.system('cat ssh_conf | sudo tee -a /etc/ssh/ssh_config >> /dev/null')

with open("/etc/ssh/ssh_config", 'r') as b:
    for num, line in enumerate(b,1):
        if "p-tag-node4" in line:
            n=num+4
            cmd="sudo sed '{},{}d' /etc/ssh/ssh_config>ssh_config".format(num,n)
            cr=("sudo rm /etc/ssh/ssh_config")
            mv=("sudo mv ssh_config /etc/ssh/")
            os.system(cmd)
            os.system(cr)
            os.system(mv)


        
