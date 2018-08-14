#!/usr/bin/python

import os
import subprocess
import sys
import urllib

#global variables
global url
global ovpnPin
global ovpnProfFile
global vpnConUUID


#check to see if user is root
def checkUser():
    if( os.geteuid() != 0 ):
        print('not signed in as root')
        sys.exit()

def clearNmConns():
    vpnConUUID = subprocess.check_output("nmcli -t -f UUID,TYPE con | grep vpn | awk -F: '{printf$1}'", shell=True)
    subprocess.call(['nmcli', 'connection', 'delete', vpnConUUID])
    subprocess.call(['rm', '-f', '/etc/NetworkManager/system-connections/*'])
    subprocess.call(['service', 'NetworkManager', 'restart'])

def downloadZipProfile():
    #get base filename
    #ovpnProfFile = '$(basename "{0}")'.format(url)
    # = os.system(ovpnProfFile)
    #make wget call to global url from getArgs() and save to tmp dir
    global url
    global filename
    urllib.urlretrieve(url,filename="/tmp/vpnprofile.zip")
    #zipFileName = subprocess.check_call('wget -{0} -P /tmp'.format(url))
    #subprocess.check_call(call)
    #unzip file
    ovpnProfFile = os.system('cd /tmp && unzip -p vpnprofile.zip > vpnprofile.ovpn')


def getArgs():
    print(sys.argv)
    index = 0
    args = sys.argv
    args.pop(0)
    print(args)
    print(args[1])
    for i in range(0, len(args),2): #parse all args
        arg = args[i]
        print(arg)
        print(i)
        #args[i] = sys.argv[i]
        #args[i] = sys.argv[i+1] #grab args following - command line arg
        if arg == '-h' or arg == '--h':
            print('The following arguments can be passed to the script')
            print('help -h or --h')
            print('file -f <file> or --f <file>')
            print('url -u <url> or --u <url>')
            sys.exit()
        #elif sys.argv[i] = '-f' or '--f':
            #ovpnProfFile = sys.argv[i+1]
        elif arg == '-u' or arg == '--u':
            global url
            url = args[args.index(arg) + 1]
            print('checking url')
            print(url)
        elif arg == '-p' or arg == '--p':
            global ovpnPin
            ovpnPin = args[args.index(arg) + 1]
            print('ovpnVerification')
            print(ovpnPin)
            #ensure pin is a number
            if ovpnPin.isdigit():
                print('Pin is a number')
            else:
                print('Pin is not a number')
                sys.exit()
        else:
            print('invalid args')
            sys.exit()

def installOpenVpn():
    #check successfull openVPN install
    #if  subprocess.check_call(['apt-get', 'install', '-y', 'openvpn']):
    if  subprocess.check_call(['apt-get', 'install', '-y', 'openvpn','unzip','network-manager-openvpn','openvpn-systemd-resolved', 'tmux', 'iptables-persistent']):
        #if unsuccessful, provide returncall and custom message
        print('open vpn failed to install')
    else:
        print('open vpn installed')

def checkExists(drct,fil):
    #check if dir exists
    if(os.path.isdir(drct)):
        print('dir exists')
    #create directory if it doesn't exist
    else:
        os.mkdir(drct)

    #check if file exists
    if(os.path.isfile(fil)):
        print('file exists')
    #create file if it doesn't exist
    else:
        print('file does not exist')
        f= open(fil,"w+")
        f.close()


def importVpnProfile():
    #check for root /root/openvpn/ dir
    checkExists('/root/openvpn/', '/root/openvpn/creds')
    f = open("/root/openvpn/creds","w+")
    f.write("vpn.secrets.password:{0}".format(ovpnPin))
    f.close()
    #populate creds file
    #subprocess.check_call('echo "vpn.secrets.password:{0}" > /root/openvpn/creds').format(str(ovpnPin))

    #import Open VPN profile
    print('i would have imported the profile but you killed me')
    subprocess.call(['nmcli','connection', 'import', 'type', 'openvpn', 'file', '/tmp/vpnprofile.ovpn'])
    os.system('echo "vpn.secrets.password:{0}" > /root/openvpn/creds'.format(ovpnPin))

    #first connection attempt
    vpnConUUID = subprocess.check_output("nmcli -t -f UUID,TYPE con | grep vpn | awk -F: '{printf$1}'", shell=True)
    print('conUUID='+str(vpnConUUID))
    subprocess.call(['nmcli', 'connection', 'up', 'uuid', vpnConUUID, 'passwd-file', '/root/openvpn/creds'])

def main():
    #check the user
    checkUser()
    #get command line args
    getArgs()
    #clear network manager of vpn connections
    clearNmConns()
    #Install Open VPN
    installOpenVpn()
    #download zip file
    downloadZipProfile()
    #import VPN profile
    importVpnProfile()



if __name__ == "__main__":
    main()
