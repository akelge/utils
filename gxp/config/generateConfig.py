#!/usr/bin/python
import os, re

path_base = ""
path_clients = path_base + "generateConfigData/"
path_results = path_base + "generateConfigResults/"
path_exec = path_base.replace(" ","\ ") + "./encode.sh $MAC $CONFIG $RESULT"
path_config = path_base + 'generateConfigData/gxp_config_CUBE'
path_config_current = "%s.tmp" % path_config

data_mac = 'DATA_MAC' ; data_user = 'DATA_USER'
data_id = 'DATA_ID' ; data_password = 'DATA_PASSWORD'

def replacePattern(value,data):
    output = value
    output = output.replace("$USER",data.get(data_user))
    output = output.replace("$ID",data.get(data_id))
    output = output.replace("$PASSWORD",data.get(data_password))
    output = output.replace("$MAC",data.get(data_mac))
    return output

print '--------------------------------------------------------------'
print "Generate CUBE GXP-2000 Configs"
print '--------------------------------------------------------------'
#READ CONFIG
print "Read config > \"%s\"" % path_config
f = open(path_config,'r')
config = f.read()
f.close()

dir_clients=os.listdir(path_clients)
counter = 0
for client in dir_clients:
    if client.endswith('.client'):
        print '--------------------------------------------------------------'
        print 'Client %s' % client.replace('.client','').upper()

        #READ DATA
        print "\tRead client data > \"%s\"" % (path_clients + client)
        data = {}
        f = open(path_clients + client,'r')
        for line in f:
	    if re.match('\s*#|^\s*$',line): continue
            try:
                d = line.split('=')
                data[d[0].strip()] = d[1].strip()
            except:
                pass
        f.close()
        data[data_mac] = data.get(data_mac).lower()
        print "\tData: %s [%s] [%s]" % (data.get(data_user),data.get(data_id),data.get(data_mac))
        print "\tData: %s custom lines" % (len(data)-4)



        #CUSTOMIZE CONFIG
        print "\tCustomizing config"
        for key,value in data.items():
            if not key.startswith("DATA"):
                value = replacePattern(value,data)
                pattern = "%s\s*=[^\n\r]*" % key
                replace = "%s = %s" % (key,value)
                config = re.sub(pattern,replace,config)

        #SAVE TMP CONFIG
        print "\tSaving client config > \"%s\"" % path_config_current
        f = open(path_config_current,'w')
        f.write(config)
        f.close()


        #EXEC ENCODE
        command = path_exec
        command = command.replace('$MAC',data.get(data_mac).replace(" ","\ "))
        command = command.replace('$CONFIG',path_config_current)
        command = command.replace('$RESULT',path_results.replace(" ","\ ")+'cfg'+data.get(data_mac))
        print '\tExecuting:\t %s' % command#.replace(" ","\n\t\t\t")
        os.system(command)
        #EXEC!!!

        print "\tDeleting client config > \"%s\"" % path_config_current
        os.unlink(path_config_current)
        counter+=1
print '--------------------------------------------------------------'
print "Done %s clients" % counter
