import os
i=1
node_name='p-tag-node'
while True:
    with open('nodes') as n:
        nd=node_name+str(i)
        if nd not in n.read():
            print(nd)
            break
        else:
            i+=1



#cmdip='openstack server list | grep {} | cut -d"|" -f"5" | cut -d"=" -f"2">temp_ip'.format(noden)
            #os.system(cmdip)
            #with open("temp_ip") as f:
            #    ip = str(f.read())
            #host = "Hostname " + ip 
            #Host = "      HOST " + noden + "\n"
            #with open('ssh_conf', 'w') as f:
            #    f.write(Host)
            #os.system('cat ssh_temp>>ssh_conf')
            #with open('ssh_conf', 'a') as f:
            #    f.write("\n      ")
            #    f.write(host)
            #    f.write("\n")
            #os.system('cat ssh_conf | sudo tee -a /etc/ssh/ssh_config >> /dev/null')
    
