#!/bin/sh

#TITLE: Отобразить информацию об операционной системе

# Заголовок скрипта. Аргументы командной строки передаются автоматически в указанном порядке
#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
HOST=$1
USERNAME=$2
PASSWORD=$3
HOSTNAME=$4
GROUPNAME=$5

echo
echo "$GROUPNAME. $HOSTNAME"
echo "=========================================="
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USERNAME@$HOST 'screenfetch'
