#!/bin/bash -

#Copyright (C) 2016  Juan Pablo Orradre
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

#Script variables
IP_BCK=192.168.1.253
PATH_LOC=/mnt/datos
PATH_ARRAY=( "/home/jp/Documentos" "/home/jp/Otros" "/home/jp/Owncloud" )
TO_BACKUP="ARRAY"
PATH_BCK=respaldos/jp
PASS_FILE=/home/jp/Documentos/Claves/.passFTP
UPL_METH="FTP"
MAX_RETRIES=20
USR_SRV_UPL=ftp
MAIN_LOG=/var/log/backup.log


function log {
	echo `date +"%d-%m-%y %H:%I:%S"`" - "$1 >> $MAIN_LOG
	echo $1
}

#Test connection
function test_conn {
	CONN_TMP=`mktemp`
	CONN=1

	nc $1 $2 < /dev/null 2>>$CONN_TMP 1>>$CONN_TMP

	grep $3 "$CONN_TMP" 1>/dev/null || CONN=0

	return $CONN;
} 


#FTP
function ftp_backup {

	if test_conn $IP_BCK 21 "FTP" -eq 0 ; then
		log "[ERROR] Can't connect remote server. Aborting backup";
		exit 1;	
	fi
	#Checks whether required function exists
	command -v lftp >/dev/null 2>&1 || log "[ERROR] The local system does not have lftp command. Aborting backup.";

        DIR_BCK_LOG=/var/log/backup_$2.log
        touch $DIR_BCK_LOG
        chmod 600 $DIR_BCK_LOG

        lftp -e "set ftp:list-options -a; mirror -cRPv $1 $PATH_BCK/$2 --delete --log=$DIR_BCK_LOG; exit;" -u $USR_SRV_UPL,$3 ftp://$IP_BCK;
}

#SSH with key access
function ssh_backup {

	if test_conn $IP_BCK 2892 "SSH" -eq 0 ; then
		log "[ERROR] Can't connect remote server. Aborting backup";
		exit 1;	
	fi

	#Checks whether required function exists
	command -v rsync >/dev/null 2>&1 || log "[ERROR] The local system does not have rsync command. Aborting backup."
	# Trap interrupts and exit instead of continuing the loop
	trap "echo Exited!; exit;" SIGINT SIGTERM
	i=0
	# Set the initial return value to failure
	false
	
 	while [ $? -ne 0 -a $i -lt $MAX_RETRIES ]
 	do
 		i=$(($i+1))
		rsync --backup --backup-dir=`date +%Y.%m.%d` --delete --progress --log-file=/var/log/resp$2.log --rsh="ssh -c arcfour -l $USR_SRV_UPL" -a $1 $PATH_BCK/$2
	done
 
	if [ $i -eq $MAX_RETRIES ]; then
  		log "[ERROR] Hit maximum number of retries, giving up.";
		exit 1;
	fi
}

function backup {
	
	if [[ ! -f $PASS_FILE ]]; then
		log "[ERROR] The file containing server pass doesn't exist on ($PASS_FILE)";		
		exit 1;
	fi

	#Loads server pass from respective file
	PASS=`cat $PASS_FILE`
	
    	#Backups the current folder
	log "[INFO] Started to backup folder  "$1;	
	DIR_NAME=`echo "$1" | sed 's|\/| |g' | awk '{print $NF}'`;

	if [[ $UPL_METH = "FTP" ]]; then
		ftp_backup "$1" "$DIR_NAME" "$PASS" || exit 1
	elif [[ $UPL_METH = "SSH" ]]; then
		ssh_backup "$1" "$DIR_NAME" "$PASS" || exit 1
	else
		log "[ERROR] Incorrect backup protocol specified.";
		exit 1;
	fi
	
	#Ends uploading folder
	log "[INFO] Ended to backup folder "$1;
	
}


touch $MAIN_LOG
chmod 600 $MAIN_LOG

# Backup process start
log "[INFO] Starts backup";


# Iterates selected folders mirroring them to their server images
if [[ $TO_BACKUP = "LOCAL" ]]; then

        log "[INFO] Local folder backup is going to start";

	for DIR in $PATH_LOC/*/ ; do

		backup $DIR || (log "[ERROR] Backup was not done due to errors. Check logs for more information." && exit 1); 
	
	done;

else

        log "[INFO] Selected folders backup is going to start";

	for DIR in "${PATH_ARRAY[@]}" ; do

		backup $DIR || (log "[ERROR] Backup was not done due to errors. Check logs for more information." && exit 1); 
	
	done;
fi


log "[INFO] Backup has successfully ended" 


exit 0;

