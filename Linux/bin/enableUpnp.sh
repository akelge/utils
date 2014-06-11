#!/bin/sh
# -*- coding: utf-8 -*-

# Copyright by Andrea Mistrali <andre@eimalta.com>
# First version: 2014-03-04T16:12 CET (+0100)
#
# Synopsis: Open uPNP ports
#
# $Id$

port=63728
url=`upnpc -P|grep desc: |cut -d" " -f 3`
upnpc -u ${url} -r $port tcp
upnpc -u ${url} -r $port udp

# vim: set ts=4 sw=4 tw=79 ft=sh :

