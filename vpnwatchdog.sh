#!/bin/bash

#VPN watchdog for YAC-VPN link using NMCLI
#Author: Dominik Piasecki
#dominik.piasecki@dpsrr.com
#  ¯\_(ツ)_/¯

#setting the vars
vpn_host_int=""
vpn_host_ext=""
credsfile=""
vpn_user=""
internet="unreachable"
failedpings=0
sleeptime=60
logfile=/var/log/vpnwatchdog.log
retain_num_lines=2000   #how many lines should the logfile hold?
fwrule=0
#getting the VPN UUID and tun device from NMCLI  \/
vpn_uuid="$(nmcli -t -f UUID,TYPE con | grep vpn | awk -F: '{print $1}')"
vpn_dev="$(nmcli -t -f DEVICE,TYPE con | grep tun | awk -F: '{print $1}')"
# END OF VARS


# set LOGFILE to the full path of your desired logfile; make sure
# you have write permissions there. set RETAIN_NUM_LINES to the
# maximum number of lines that should be retained at the beginning
# of your program execution.
# execute 'logsetup' once at the beginning of your script, then
# use 'log' how many times you like.

function logsetup() {
  TMP=$(tail -n $retain_num_lines $logfile 2>/dev/null) && echo "${TMP}" > $logfile
  exec > >(tee -a $logfile)
  exec 2>&1
}

function log() {
  TMP=$(tail -n $retain_num_lines $logfile 2>/dev/null) && echo "${TMP}" > $logfile
  echo "[$(date --rfc-3339=seconds)]: $*"
}
#create the logfile and redirect output from "log" function to echo
logsetup

#wait for the internet to come up, do not try VPNcon until external address of vpn server is reachable
function check_inet() {
  while [[ $internet == "unreachable" ]]; do
    log "Please stand by..."
    sleep $sleeptime
    ping -c 1 $vpn_host_ext >/dev/null 2>&1
    if [[ $? -ne 0 ]]; then
      log "Ext VPN address not reachable, waiting for cell link. Trying again!"
    else
      internet="reachable"
    fi
  done
}

#try to initially establish the VPN connection before running the watchdog
function vpn_up() {
  log "Initial VPN connection attempt..."
  nmcli connection up $vpn_uuid passwd-file $credsfile
  sleep $sleeptime
  #set the VPNdev this can only happen after the VPN tunnel is activated
  vpn_dev="$(nmcli -t -f DEVICE,TYPE con | grep tun | awk -F: '{print $1}')"
}

function check_fw() {
  #check all rules exists
  iptables -C OUTPUT -m owner --gid-owner $vpn_user -o lo -j ACCEPT || fwrule=1
  iptables -C OUTPUT -m owner --gid-owner $vpn_user \! -o $vpn_dev -j REJECT || fwrule=1
  iptables -C OUTPUT -o lo -j ACCEPT || fwrule=1
  iptables -C INPUT -i lo -j ACCEPT || fwrule=1
  iptables -C INPUT -p tcp -m tcp --dport 22 -j ACCEPT || fwrule=1
  iptables -C INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT || fwrule=1
  iptables -C INPUT -p tcp --dport 12345 -j ACCEPT || fwrule=1
  iptables -C INPUT -j DROP || fwrule=1
  log "You may get an error here, this is expected please remain calm."
  #ipt_rules="$(($rule1+$rule2+$rule3+$rule4+$rule5+$rule6+$rule7))"
  sleep 5

  if [[ fwrule -ne 0 ]]; then
    log "Failed to find rule(s)  (0/1):
              1:$rule1 2:$rule2 3:$rule3 4:$rule4 5:$rule5 6:$rule6 7:$rule7"
    iptables -F   #flush iptables of all rules
    #setup the chain (allow all outgoing/established deny all incoming except SSH)
    iptables -A OUTPUT -m owner --gid-owner $vpn_user -o lo -j ACCEPT
    iptables -A OUTPUT -m owner --gid-owner $vpn_user \! -o $vpn_dev -j REJECT
    iptables -A OUTPUT -o lo -j ACCEPT
    iptables -A INPUT -i lo -j ACCEPT
    iptables -A INPUT -p tcp -m tcp --dport 22 -j ACCEPT
    iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
    iptables -A INPUT -p tcp --dport 12345 -j ACCEPT
    iptables -A INPUT -j DROP

    #make the FW rules persistant (requires iptables-persistent to set on boot)
    iptables-save > /etc/iptables/rules.v4
  else
    log "Firewall appears to be configured correctly, nothing done."
  fi
}

#run the VPN connection watchdog test/restore in infinite loop reboot/restore after X failed
function watchdog() {
  while [[ true ]]; do
    sleep $sleeptime
    #check the connection, if bad try and bring up the connection
    ping -c 1 $vpn_host_int >/dev/null 2>&1
    if [[ $? -ne 0 ]]; then   #if ping is nonzero...
      log "Internal VPN address not reachable, trying to set up us the bomb."
      log "Number of consecutive failed attempts: $failedpings"
      failedpings=$[failedpings + 1]
      log "Bringing the VPN down for reset"
      nmcli connection down $vpn_uuid
      log "Trying to bring the connection back, please stand by."
      sleep $sleeptime
      nmcli connection up $vpn_uuid passwd-file $credsfile
      sleep 5
    else
      log "vpn happy!   :D"
      failedpings=0
    fi

    if [[ $failedpings -gt 9 ]]; then
      failedpings=0
      log "Server is unreachable, rebooting"
      sleep $sleeptime
      reboot
    fi
  done
}

#start of execution
log "==> VPN Watchdog current configuration:
  User  :$vpn_user
  UUID  :$vpn_uuid
  ExtIP :$vpn_host_ext
  IntIP :$vpn_host_int
  <=="
log "==> Checking network connection <=="
check_inet
log "==> Bringing up the VPN <=="
vpn_up
log "==> Checking FW Rules <=="
check_fw
log "==> Starting the watchdog <=="
watchdog


log "If you ever see this message some really bad shit happened.... EOF"
