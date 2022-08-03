import os
#noden = 'p-tag-node1'
#Host = "      HOST " + noden + "\n"
#with open('ssh_conf', 'w') as f:
#    f.write(Host)
#os.system('cat ssh_temp>>ssh_conf')
with open("temp_ip") as f:
    ip = str(f.read())
host = "Hostname " + ip + "\n" 
#with open('ssh_conf', 'a') as f:
 #   f.write("\n      ")
 #   f.write(host)
#os.system('cat ssh_conf | sudo tee -a /etc/ssh/ssh_config >> /dev/null')

with open("hosts", 'r+') as b:
    ll=b.readlines()
    ll.insert(6,host)
    b.seek(0)
    b.writelines(ll)

        
