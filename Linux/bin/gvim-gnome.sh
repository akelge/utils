#!/bin/bash
# -*- coding: utf-8 -*-

# Copyright by Andrea Mistrali <andre@eimalta.com>
# First version: 2014-02-20T10:43 CET (+0100)
#
# Synopsis: Gvim wrapper
#
# $Id$



# vim: set ts=4 sw=4 tw=79 ft=sh :

echo "Starting gvim..."
y="$*"


if [ -f "$y" ];then
    echo "arg $y"
    gvim --servername GVIM --remote-tab-silent "$y"
else
    echo "no args"
    # is gvim server already active?
    echo "looking for list"
    gvim --serverlist |grep -q GVIM
    if [ "$?" -eq "1" ]; then
        echo "no server, start new one"
        gvim --servername GVIM
    else
        echo "server, start new tab"
        gvim --servername GVIM --remote-send ":tabnew<CR>"
    fi
fi

echo "done..."
exit 0
