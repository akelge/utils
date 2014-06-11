#!/bin/sh
# -*- coding: utf-8 -*-

# Copyright by Andrea Mistrali <akelge@gmail.com>
# First version: 2014-03-03T19:21 CET (+0100)
#
# Synopsis: Touchpad Settings for games
#
# $Id$

status=$1

usage() {
    echo "Usage: `basename $0` [on|off]"
    exit 2
}

case $status in
    on) echo Game mode: on
        synclient TapButton1=0 TapButton2=0 TapButton3=0
        killall syndaemon
        ;;
    off) echo Game mode: off
        synclient TapButton1=1 TapButton2=3 TapButton3=2
        syndaemon -k -i .6 -R -d
        ;;
    *) usage
        ;;
esac

# synclient TapButton2=3 TapButton3=2

