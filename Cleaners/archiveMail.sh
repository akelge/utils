#!/bin/sh
# -*- coding: latin-1 -*-

# Copyright by Andrea Mistrali <am@am.cx>.
# First version: 02:lug:2008 17:24
#
# Synopsis: Sync imap servers
#
# $Id$

LOGFILE="/var/log/archiveMail.log"

SERVER="zeus.oob"
USER1="__public__"
USER2="__archive__"
AUTHUSER="dm"
PASS="chpwd"

if [ "$1" == "-h" ]; then
    cat<<EOB

`basename $0` [-h] [<folder>]

 -h print this help

if no folder is specified archive all #Public folders

EOB
exit 0
elif [ "x$1" != "x" ]; then
    FLIST="--folder '#Public/$1'"
else
    FLIST="--folderrec '#Public/'"
fi

echo -n "Sync mail "

imapsync \
    --host1 ${SERVER} \
    --user1 ${USER1} \
    --authuser1 ${AUTHUSER} \
    --password1 ${PASS} \
    --authmech1 PLAIN \
    --host2 ${SERVER} \
    --user2 ${USER2} \
    --authuser2 ${AUTHUSER} \
    --password2 ${PASS} \
    --authmech2 PLAIN \
    --syncinternaldates \
    --syncacls \
    --minage 365 \
    $FLIST \
    --prefix1 "#Public" \
    --prefix2 "#Archive" \
    --exclude "Spam.*" \
    --expunge \
    --delete \
    --useheader "Message-ID" \
    --useheader "Subject" >> $LOGFILE 2>&1


if [ $? != 0 ]; then
    echo "FAILURE"
else
    echo "SUCCESS"
fi
