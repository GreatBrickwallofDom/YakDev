#!/usr/bin/python

import os
import subprocess
import sys

#global variables
global url
global ovpnPin
global ovpnProfFile
global vpnConUUID


#check to see if user is root
def checkUser():
    if( os.geteuid() != 0 ):
        print('not signed in as root')


def downloadZipProfile():
    #get base filename
    #ovpnProfFile = '$(basename "{0}")'.format(url)
    # = os.system(ovpnProfFile)
    #make wget call to global url from getArgs() and save to tmp dir
    zipFileName = subprocess.check_call('wget -{0} -P /tmp'.format(url))
    subprocess.check_call(call)
    #unzip file
    ovpnProfFile = subprocess.check_call('cd /tmp && unzip {0}'.format(zipFileName))


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
    if  subprocess.check_call(['apt-get', 'install', '-y', 'openvpn']):
    #if  subprocess.check_call(['apt-get', 'install', '-y', 'openvpn','unzip','network-manager-openvpn','openvpn-systemd-resolved', 'tmux']):
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
    #populate creds file
    subprocess.check_call('echo > /root/openvpn/creds').format(ovpnPin)

    #import Open VPN profile
    subprocess.check_call('nmcli connection import type openvpn {0} /tmp/{0}'.format(ovnpProfFile))
    subproccess.check_call('echo "vpn.secrets.password:{0}" > /vpn/pin/location'.format(ovpnPin))

    #first connection attempt
    vpnConUUID = subproccess.check_call("nmcli -t -f UUID,TYPE con | grep vpn | awk -F: '{print$1}'")
    subproccess.check_call('nmcli connection up {0} passwd-file ~/vpn/pin/location'.format(vpnConUUID))

def main():
    #check the user
    checkUser()
    #get command line args
    getArgs()
    #Install Open VPN
    installOpenVpn()
    #import VPN profile
    importVpnProfile()



if __name__ == "__main__":
    main()
