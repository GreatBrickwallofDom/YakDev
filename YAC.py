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
    if( os.getlogin() != 'root' ):
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
    args = {} #empty dictionary for command line args
    for i in sys.argv: #parse all args
        #args[i] = sys.argv[i]
        #args[i] = sys.argv[i+1] #grab args following - command line arg
        if sys.argv[i] = '-h' or '--h':
            print('The following arguments can be passed to the script')
            print('help -h or --h')
            print('file -f <file> or --f <file>')
            print('url -u <url> or --u <url>')
        #elif sys.argv[i] = '-f' or '--f':
            #ovpnProfFile = sys.argv[i+1]
        elif sys.argv[i] = '-u' or '--u':
            url = sys.argv[i+1]
        elif sys.argv[i] = '-p' or '--':
            ovpnPin = sys.argv[i+1]
            #ensure pin is a number
            if ovpnPin.isdigit():
            else:
                print('Pin is not a number')
                sys.exit()
        else:
            print('invalid args')
         

def installOpenVpn():
    #check successfull openVPN install
    if ( subprocess.check_call('apt-get ]install -y openvpn unzip network-manager-openvpn openvpn-systemd-resolved') != 0 ):
        #if unsuccessful, provide returncall and custom message
        print('open vpn failed to install')

def checkExists(dir,fil):
    #check if dir exists
    if(os.path.isdir(dir)):
    #create directory if it doesn't exist
    else:
        subprocess.check_call('mkdir {0}'.format(dir))

    #check if file exists
    if(os.path.isfile(fil)):
    #create file if it doesn't exist
    else:
        subprocess.check_call('touch {0}'.format(fil))


def importVpnProfile():
    #check for root /root/openvpn/ dir
    checkExists('/root/openvpn/', null)
    #check for /root/openvpn/creds file
    checkExists(null, '/root/openvpn/creds')
    #populate creds file
    subprocess.check_call('echo "{0}" > /root/openvpn/creds'.format(ovpnPin))

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
    checkArgs()
    #Install Open VPN
    installOpenVpn()
    #import VPN profile
    importVpnProfile()
    


if __name__ == "__main__":
    main()