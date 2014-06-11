#!/bin/sh
# -*- coding: utf-8 -*-

# Copyright by Andrea Mistrali <akelge@gmail.com>
# First version: 2014-04-04T08:36 CEST (+0200)
#
# Synopsis: Things to do when GNOME3 session starts
#
# $Id$
LOG=~/.session.log
#echo > ~/.session.log

log() {
date=`date +"%Y/%m/%d %T,%N"`
echo "$date sessionStart.sh $*" >> $LOG
}

# Remark to enable middle-button
# log "enable middle button in gnome"
#gsettings set org.gnome.settings-daemon.peripherals.mouse middle-button-enabled true
#gsettings set org.gnome.settings-daemon.plugins.mouse active false
#gsettings set org.gnome.settings-daemon.peripherals.touchpad horiz-scroll-enabled true


# Enable three finger tap for middle click and two finger tap for right click
log 'setting touchpad taps'
synclient TapButton2=3 TapButton3=2
synclient HorizTwoFingerScroll=1

log 'start syndaemon kbd tracking'

#syndaemon -k -i .6 -R -d

# Start autocutsel, fork and ignore selection when button1 is down
killall autocutsel > /dev/null 2>&1
log 'starting autocutsel on CLIPBoARD'
autocutsel -fork -buttonup
log 'starting autocutsel on PRIMArY'
autocutsel -fork -buttonup -s PRIMARY

# # Remove DASH

# sleep 10
# log "removing dash"
# dbus-send --session --type=method_call --dest=org.gnome.Shell /org/gnome/Shell org.gnome.Shell.Eval string:'Main.overview._dash.actor.hide();'

# log "kill chrome and restart it"
# killall chrome
# killall chrome

# log "start skype"
# sleep 5

# log "start skype IT"
# env PULSE_LATENCY_MSEC=60  skype
# sleep 5
# env PULSE_LATENCY_MSEC=60 skype --dbpath=~/.Skype-IT %U
# vim: set ts=4 sw=4 tw=79 ft=sh :


