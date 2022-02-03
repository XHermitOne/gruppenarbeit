#!/bin/sh

#TITLE: Установить дополнительное программное обеспечение

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

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USERNAME@$HOST "echo $PASSWORD | sudo -S apt install --assume-yes screenfetch"
