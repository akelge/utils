#!/bin/sh
# -*- coding: latin-1 -*-

# Copyright by Andrea Mistrali <am@am.cx>.
# First version: 02:lug:2008 17:24
#
# Synopsis: Sync imap servers
#
# $Id$

LOGFILE="/var/log/archiveMail.log"
LIST="/usr/local/lib/archiveMail/folders.lst"

SERVER="zeus.oob"

USER="__public__"
AUTHUSER="dm"
PASS="chpwd"

if [ "$1" == "-h" ]; then
    cat<<EOB

`basename $0` [-h] [<folder>]

if no folder is specified get folders from:
    $LIST

EOB
exit 0
elif [ "x$1" != "x" ]; then
    FLIST=$1
else
    FLIST=`cat $LIST`
fi

for folder in $FLIST;do
    echo -n "Processing folder $folder: "
    imapsync \
        --host1 ${SERVER} \
        --user1 ${USER} \
        --authuser1 ${AUTHUSER} \
        --password1 ${PASS} \
        --authmech1 PLAIN \
        --host2 ${SERVER} \
        --user2 ${USER} \
        --authuser2 ${AUTHUSER} \
        --password2 ${PASS} \
        --authmech2 PLAIN \
        --syncinternaldates \
        --syncacls \
        --minage 365 \
        --folder "#Public/$folder" \
        --prefix1 "#Public" \
        --prefix2 "#Archive" \
        --expunge \
        --delete \
        --useheader 'Message-ID' \
        --useheader 'Subject' >> $LOGFILE 2>&1
    if [ $? == 0 ]; then
        echo "SUCCESS"
    else
        echo "FAILURE"
    fi
done 
