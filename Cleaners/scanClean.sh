#!/bin/sh
# -*- coding: latin-1 -*-

# Copyright by Andrea Mistrali <am@am.cx>
# First version: 2010-11-09T11:10 CET (+0100)
# Last modified: 2010-12-27T10:24 CET (+0100)
#
# Synopsis: Clean SCAN folder
#
# $Id$

DEBUG="echo"
SCAN="/Docs/SCAN"

cd $SCAN

for user in *; do
    echo Processing $user
    cd $user
    cat<<EOB > /tmp/$user.mail

**************************
** Scan Cleaner  Report **
**************************

Le scansioni più vecchie di 28 giorni sono state rimosse.

*****************************************************************
**            Lista delle scansioni eliminate                  **
*****************************************************************
|||     DATA DI CREAZIONE           ||           NOME FILE    |||
EOB

# 28 days
    find . -type f -name "[a-zA-Z0-9]*" -mtime +28 -exec  stat -c"%y || %n" {} ";" >> /tmp/$user.mail
    find . -type f -name "[a-zA-Z0-9]*" -mtime +28 -exec  rm -v {} ";" > /dev/null

    cat<<EOB >> /tmp/$user.mail

*****************************************************************
** Lista delle scansioni che verranno cancellate tra 7 giorni  **
*****************************************************************
|||     DATA DI CREAZIONE           ||           NOME FILE    |||
EOB

# 21 days
    find . -type f -name "[a-zA-Z0-9]*" -mtime +21 -exec  stat -c"%y || %n" {} \; > /tmp/$user.21.txt
# 14 days
    find . -type f -name "[a-zA-Z0-9]*" -mtime +14 -exec  stat -c"%y || %n" {} \; > /tmp/$user.14.txt

    cat /tmp/$user.21.txt /tmp/$user.14.txt|sort|uniq -d >> /tmp/$user.mail

    cat<<EOB >> /tmp/$user.mail

*****************************************************************
** Lista delle scansioni che verranno cancellate tra 14 giorni **
*****************************************************************
|||     DATA DI CREAZIONE           ||           NOME FILE    |||
EOB
    cat /tmp/$user.21.txt /tmp/$user.14.txt|sort|uniq -u >> /tmp/$user.mail

cat<<EOB >> /tmp/$user.mail
--
 N.B.: Le scansioni eliminate sono recuperabili ancora per 8 giorni dal backup dei dati.

 JOB DONE - OK
EOB

    mail -a "X-Module: scanClean" -s "Scan cleaner: risultati per $user" $user < /tmp/$user.mail
    rm /tmp/$user.mail
    rm /tmp/$user.21.txt
    rm /tmp/$user.14.txt
    cd ..
done

