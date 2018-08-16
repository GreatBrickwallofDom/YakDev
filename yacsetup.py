#!/usr/bin/python

import os
import subprocess
import sys
import urllib
import urllib2
from optparse import OptionParser

#global variables
global url
global ovpnPin
global ovpnProfFile
global vpnConUUID


#check to see if user is root
def checkUser():
    if( os.geteuid() != 0 ):
        print('This script needs sudo, call me like this:!\n $ sudo python ' + sys.argv[0])
        sys.exit()

def parseArgs():
    parser = OptionParser()

    parser.add_option("-u", "--url", dest="url",
            help="URL to download the OVPN Profile")
    parser.add_option("-p", "--pin", dest="ovpnPin",
            help="Pin for the OpenVPN User")

    (options, args) = parser.parse_args()
    global url
    url = options.url
    global ovpnPin
    ovpnPin = options.ovpnPin

def menu():
    global ovpnPin
    global url
    ovpnPin = ""
    url = ""
    ovpnPin = raw_input("\nPlease enter the pin: ")
    url = raw_input("Please enter the profile url: ")

def validate():
    global ovpnPin
    global url
    #convert all into strings
    ovpnPin = str(ovpnPin)
    url = str(url)
    #trim the inputs of all spaces
    ovpnPin = ovpnPin.replace(" ", "")
    url = url.replace(" ", "")
    #Print the corrected vars for user
    print('URL: ' + url)
    print('PIN: ' + ovpnPin + "\n")
    #check if all args supplied and verify
    if (url == "None"):
        print('ERROR: The URL was not given')
        sys.exit()
    if (ovpnPin == "None"):
        print('ERROR: The PIN was not given')
        sys.exit()
    #get the url and check to make sure its valid
    print('Checking the URL, Please wait.\n')
    urlReq = ""
    urlReq = subprocess.Popen(['curl', '-s', '-o', '/dev/null', '-w', '"%{http_code}"', url], stdout=subprocess.PIPE)
    urlReqOut = urlReq.stdout.read()
    if (len(ovpnPin) < 8) or (ovpnPin.isdigit() == False) or (urlReqOut != '"200"'):
        if (len(ovpnPin) < 8):
            print('ERROR: The pin must be at least 8 digits.')
        if (ovpnPin.isdigit() == False):
            print('ERROR: The pin must be a number.')
        if (urlReqOut != '"200"'):
            print('ERROR: The URL does not appear to be valid.')
            print('HTTP ECODE: ' + str(urlReqOut))
        sys.exit()
    else:
        print('VARs validation successfull\n')

#clear network manager connections
def clearNmConns():
    vpnConUUID = subprocess.check_output("nmcli -t -f UUID,TYPE con | grep vpn | awk -F: '{printf$1}'", shell=True)
    subprocess.call(['nmcli', 'connection', 'delete', vpnConUUID])
    subprocess.call(['rm', '-f', '/etc/NetworkManager/system-connections/*'])
    subprocess.call(['service', 'NetworkManager', 'restart'])

def downloadZipProfile():
    global url
    global filename
    #fetch zip profile file from url
    urllib.urlretrieve(url,filename="/tmp/vpnprofile.zip")
    #unzip file
    ovpnProfFile = os.system('cd /tmp && unzip -p vpnprofile.zip > vpnprofile.ovpn')

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
    subprocess.call(['nmcli','connection', 'import', 'type', 'openvpn', 'file', '/tmp/vpnprofile.ovpn'])
    os.system('echo "vpn.secrets.password:{0}" > /root/openvpn/creds'.format(ovpnPin))

    #first connection attempt
    vpnConUUID = subprocess.check_output("nmcli -t -f UUID,TYPE con | grep vpn | awk -F: '{printf$1}'", shell=True)
    print('conUUID='+str(vpnConUUID))
    print('\nWaiting for the VPN connection to come up.\nIf you get an error check the pin, you may have mistyped it.')
    subprocess.call(['nmcli', 'connection', 'up', 'uuid', vpnConUUID, 'passwd-file', '/root/openvpn/creds'])

def cleanUp():
    os.remove("/tmp/vpnprofile.zip")
    os.remove("/tmp/vpnprofile.ovpn")

def main():
    #check the user
    checkUser()
    #get command line args
    parseArgs()
    if len(sys.argv) > 1:
        print("Using supplied args: \n")
    else:
        print("Menu: \n")
        menu()
    #validate the input, quit if bad
    validate()
    #clear network manager of vpn connections
    clearNmConns()
    #Install Open VPN
    installOpenVpn()
    #download zip file
    downloadZipProfile()
    #import VPN profile
    importVpnProfile()
    #clean up the /tmp/ files
    cleanUp()


if __name__ == "__main__":
    main()
