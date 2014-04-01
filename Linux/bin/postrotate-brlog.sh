#!/bin/sh
# -*- coding: utf-8 -*-

# Copyright by Andrea Mistrali <andre@eimalta.com>
# First version: 2014-03-06T16:25 CET (+0100)
#
# Synopsis: restart a BR application after log rotation
#
# $Id$

# $1 is the full path to log file

LOGFILE=$1

if [ -f $LOGFILE ]; then
    cd `dirname $LOGFILE` # /var/www/sitename/log
    cd .. # /var/www/sitename/
    touch tmp/restart.txt
else
    echo "not a log file $LOGFILE"
fi

# vim: set ts=4 sw=4 tw=79 ft=sh :

