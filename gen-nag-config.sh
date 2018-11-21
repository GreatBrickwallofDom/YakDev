#!/bin/bash

#Nagios server config generator
#Author: Dominik Piasecki
#dominik.piasecki@dpsrr.com

#
# Init our vars
#
version="1.0"
yacSerial="x"
yacIp="x"
nagServersDir="/usr/local/nagios/etc/servers"
OLDIFS=$IFS
IFS=,


#
# Define Functions
#
usage() {
  cat << EOF
Nagios Config Generator v$version
    Usage: ./gen-nag-config.sh [serial#] [ipAddr]
      -h, --help            display this help and exit
      -c, --csv             input csv file format - Serial#,internalIP
                            one line per host
Examples:
  ./gen-nag-config.sh                    Start configurator in interactive mode
  ./gen-nag-config.sh 12345 1.2.3.4      Generate config with vars provided
EOF
    #' Fix syntax highlight on sublime
    exit 1
}

function valid_ip() {
    local  ip=$1
    local  stat=1

    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        OIFS=$IFS
        IFS='.'
        ip=($ip)
        IFS=$OIFS
        [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 \
            && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
        stat=$?
    fi
    return $stat
}

function readHostInfo() {
	read -p "YAC Serial # (exclude the Y): " -n 5 -r
  yacSerial="$REPLY"
	echo ""
	read -p "YAC Internal IP address: " -r
	yacIp=$REPLY
	echo ""
	validate $yacSerial $yacIp
}

function readCsv() {
	if [[ ! -f $1 ]]; then
		echo "$1 file not found"
		exit 1
	fi
	while read sn ip
	do
		echo "Ser : $sn"
		echo "IP  : $ip"
		validate $sn $ip
		writeConfig
	done < $1
	IFS=$OLDIFS
}

function validate() {
	if [[ ${#1} == 5 ]] && [[ "$1" =~ ^[0-9]+$ ]]; then
		yacSerial="$1"
	else
		printf "\nERR: Serial # [$1] is invalid\n"
		exit 1
	fi
	if valid_ip $2; then
		yacIp="$2"
	else
		echo "ERR: IP Addr [$2] appears invalid"
		exit 1
	fi
	printf "VARs Valid, generating config\n\n"
}

function writeConfig() {
	if [[ "$yacSerial" = x ]] || [[ "$yacIp" = x ]]; then
		printf "\nERR: VARs Unset exiting!"
		exit 1
	fi
	echo "
	define host {
		use                             linux-server
	        host_name                       Y$yacSerial
	        alias                           NS YAC $yacSerial
	        address                         $yacIp
		check_command			check_nrpe!check_host
	        max_check_attempts              5
	        check_period                    24x7
	        notification_interval           30
	        notification_period             24x7
	        notifications_enabled           1
	        notification_options            d,u,r,f,s
	#        register                        0
	        contact_groups          	admins
	}


	define service {
	    use                     local-service           ; Name of service template to use
	    host_name               Y$yacSerial
	    service_description     Disk
	    check_command           check_nrpe!check_disk
	}

	define service {
	    use                     local-service           ; Name of service template to use
	    host_name               Y$yacSerial
	    service_description     Users
	    check_command           check_nrpe!check_users
	}

	define service {
	    use                     local-service           ; Name of service template to use
	    host_name               Y$yacSerial
	    service_description     Total Processes
	    check_command           check_nrpe!check_total_procs
	}

	define service {
	    use                     local-service           ; Name of service template to use
	    host_name               Y$yacSerial
	    service_description     Load
	    check_command           check_nrpe!check_load!5.0,4.0,3.0!10.0,6.0,4.0
	}

	define service {
	    use                     local-service           ; Name of service template to use
	    host_name               Y$yacSerial
	    service_description     Swap Usage
	    check_command           check_nrpe!check_swap
	}

	define service {
	    use                     local-service           ; Name of service template to use
	    host_name               Y$yacSerial
	    service_description     SSH
	    check_command           check_ssh
	}

	define service {
	    use                     local-service
	    host_name               Y$yacSerial
	    service_description     24V Supply
	    check_command	    check_nrpe!check_v24
	}

	define service {
	    use                     local-service
	    host_name               Y$yacSerial
	    service_description     Battery
	    check_command           check_nrpe!check_battery
	}

	define service {
	    use                     local-service
	    host_name               Y$yacSerial
	    service_description     5V Supply
	    check_command           check_nrpe!check_v5
	}

	define service {
	    use                     local-service
	    host_name               Y$yacSerial
	    service_description     3.3V Supply
	    check_command           check_nrpe!check_v33
	}

	define service {
	    use                     local-service
	    host_name               Y$yacSerial
	    service_description     Insulated Box Temp
	    check_command           check_nrpe!check_boxtemp
	}

	define service {
	    use                     local-service
	    host_name               Y$yacSerial
	    service_description     Air Temp
	    check_command           check_nrpe!check_airtemp
	}

	define service {
	    use                     local-service
	    host_name               Y$yacSerial
	    service_description     Case Temp
	    check_command           check_nrpe!check_casetemp
	}

	define service {
	    use                     local-service
	    host_name               Y$yacSerial
	    service_description     Humidity
	    check_command           check_nrpe!check_humidity
	}

	define service {
	    use                     local-service
	    host_name               Y$yacSerial
	    service_description     Turbine #1 Failure Count
	    check_command           check_nrpe!check_turbine1fail
	}

	define service {
	    use                     local-service
	    host_name               Y$yacSerial
	    service_description     Turbine #2 Failure Count
	    check_command           check_nrpe!check_turbine2fail
	}

	define service {
	    use                     local-service
	    host_name               Y$yacSerial
	    service_description     Turbine Run Hours
	    check_command           check_nrpe!check_turbinehrs
	}
	" > $nagServersDir/Y$yacSerial.cfg

	# Set permissions for the configuration file generated
	chown root:root $nagServersDir/Y$yacSerial.cfg
	chmod 644 $nagServersDir/Y$yacSerial.cfg

	printf "\nGenerated: \n$nagServersDir/Y$yacSerial.cfg\n\n"
}



#
# Start of execution
#
# read various flags and take actions based on input
if [[ $# -eq 0 ]]; then
	readHostInfo
	writeConfig
elif [[ "$1" = -c ]] || [[ $1 = --csv ]]; then
	echo "CSV Selected:$1
	Reading from file:$2"
	readCsv $2
	exit 0
elif [[ "$1" = --help ]] || [[ "$1" = -h ]] || [[ $# -eq 1 ]]; then
	usage
elif [[ $# -eq 2 ]]; then
	validate $1 $2
	writeConfig
else
	usage
	exit 0
fi
