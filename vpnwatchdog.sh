#!/bin/bash

#VPN watchdog for YAC-VPN link using NMCLI
#Author: Dominik Piasecki
#dominik.piasecki@dpsrr.com
#  ¯\_(ツ)_/¯

#setting the vars
vpn_host_int=""
vpn_host_ext=""
credsfile="/home/pi/openvpn/pass"
internet="unreachable"
failedpings=0
sleeptime=5
logfile=/var/log/vpnwatchdog.log
retain_num_lines=2000   #how many lines should the logfile hold?
#getting the VPN UUID from NMCLI  \/
vpn_uuid="$(nmcli -t -f UUID,TYPE con | grep vpn | awk -F: '{print $1}')"
# END OF VARS


# set LOGFILE to the full path of your desired logfile; make sure
# you have write permissions there. set RETAIN_NUM_LINES to the
# maximum number of lines that should be retained at the beginning
# of your program execution.
# execute 'logsetup' once at the beginning of your script, then
# use 'log' how many times you like.

function logsetup {
    TMP=$(tail -n $retain_num_lines $logfile 2>/dev/null) && echo "${TMP}" > $logfile
    exec > >(tee -a $logfile)
    exec 2>&1
}

function log {
    echo "[$(date --rfc-3339=seconds)]: $*"
}
#create the logfile and redirect output from "log" function to echo
logsetup

#wait for the internet to come up, do not try VPNcon until external address
#of vpn server is reachable
function check_inet() {
  while [[ $internet == "unreachable" ]]; do
    log "Checking internet connection..."
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
      #failedpings=$[failedpings + 1]
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

#Start of execution
log "Checking network connection"
check_inet
log "Bringing up the VPN"
vpn_up
log "Starting the watchdog"
watchdog


log "If you ever see this message some really bad shit happened.... EOF"
