#!/bin/bash

#Copyright (C) 2015  Juan Pablo Orradre
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

#Variables generales
IP_FTP=192.168.1.253
PATH_VMS_LOC=/mnt/datos/Listados
PATH_VMS_FTP=VMs
PASS_FILE=./.passFTP


function log {
	echo `date +"%d-%m-%y %H:%I:%S"`" - "$1 >> /var/log/respVMs.log
	echo $1
}



function respaldarVM {

	function log {
		echo `date +"%d-%m-%y %H:%I:%S"`" - "$1 >> /var/log/respVMs.log
		echo $1
	}
	
	#Levanta la clave del FTP
	PASS=`cat $PASS_FILE`
    	#Respalda la VM
	log "[INFO] Comienza a respaldar la VM "$1;	
	VMNOM=`echo "$1" | sed 's|\/| |g' | awk '{print $4}'`;

	lftp -e "mirror -cRPv $1 VMs/ --delete --log=/var/log/respVM$VMNOM.log; exit;" -u ftp,$PASS ftp://$IP_FTP

	#Termino de comprimir la VM
	log "[INFO] Termino de respaldar la VM "$1;
	
}


# Inicio de proceso
log "[INFO] Comienza respaldo de VMs";

# Recorre todas las carpetas de VMs y las respalda si es necesario
for VM in $PATH_VMS_LOC/*/ ; do

	respaldarVM $VM; 
	
done;
 
# Fin de proceso 
log "[INFO] Fin de respaldo de VMs";

exit 0;
