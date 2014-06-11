#!/bin/sh
# -*- coding: utf-8 -*-

# Copyright by Andrea Mistrali <akelge@gmail.com>
# First version: 2014-03-03T19:21 CET (+0100)
#
# Synopsis: Touchpad Settings
#
# $Id$
echo HOTPLUG > /tmp/syn.txt
synclient TapButton2=3 TapButton3=2
synclient -l >> /tmp/syn.txt


# vim: set ts=4 sw=4 tw=79 ft=sh :

