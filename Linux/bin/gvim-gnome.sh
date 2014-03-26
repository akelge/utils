#!/bin/bash
# -*- coding: utf-8 -*-

# Copyright by Andrea Mistrali <andre@eimalta.com>
# First version: 2014-02-20T10:43 CET (+0100)
#
# Synopsis: Gvim wrapper
#
# $Id$



# vim: set ts=4 sw=4 tw=79 ft=sh :

y="$*"

echo "$y"

if [ -f "$y" ];then
    gvim --servername GVIM --remote-tab-silent "$y"
else
    # is gvim server already active?
    gvim --serverlist |grep -q GVIM
    if [ "$?" -eq "1" ]; then
        gvim --servername GVIM
    else
        gvim --servername GVIM --remote-send ":tabnew<CR>"
    fi
fi
