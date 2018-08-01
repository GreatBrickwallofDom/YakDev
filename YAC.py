#!/usr/bin/python

import os
import subprocess
import sys

#global variables
global url
global ovpnPin
global ovpnProfFile

#check to see if user is root
def checkUser():
    if( os.getlogin() != 'root' ):
    os.system('echo not signed in as root) 


def downloadZipProfile():
    #get base filename
    #ovpnProfFile = '$(basename "{0}")'.format(url)
    zipFileName = os.system(ovpnProfFile)
    #make wget call to global url from getArgs() and save to tmp dir
    call = 'wget -{0} -P /tmp'.format(url)
    subprocess.check_call(call)
    #unzip file
    suprocess.check_call('unzip {0}'.format(zipFileName))


def getArgs():
    

def installOpenVpn():
    #check successfull openVPN install
    if ( subprocess.check_call('apt-get install -y openvpn unzip network-manager-openvpn openvpn-systemd-resolved') != 0 ):
        #if unsuccessful, provide returncall and custom message
        os.system('echo open vpn failed to install')

def checkExists(dir,fil):
    #check if dir exists
    if(os.path.isdir(dir)):
    else:
        subprocess.check_call('mkdir {0}'.format(dir))

    #check if file exists
    if(os.path.isfile(fil)):
    else:
        subprocess.check_call('touch {0}'.format(fil))

def importVpnProfile():
    #check for root /root/openvpn/ dir
    checkExists('/root/openvpn/', null)
    #check for /root/openvpn/creds file
    checkExists(null, '/root/openvpn/creds')

    #import opnvpn profile
    subprocess.check_call('nmcli connection import type openvpn file /path/to/your.ovpn')
    subproccess.check_call('echo "vpn.secrets.password:{0}" > /vpn/pin/location'.format(ovpnPin))
    subproccess.check_call('nmcli connection up <name-of-vpn-connection> passwd-file ~/vpn/pin/location')

def main():

if __name__ == "__main__":
    main()