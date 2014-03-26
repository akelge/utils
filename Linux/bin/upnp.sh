#!/bin/sh
# -*- coding: utf-8 -*-

# Copyright by Andrea Mistrali <andre@eimalta.com>
# First version: 2014-03-04T16:12 CET (+0100)
#
# Synopsis: Open uPNP ports
#
# $Id$

upnpc -u http://172.16.10.254:2828/gateway.xml -r 63728 tcp
upnpc -u http://172.16.10.254:2828/gateway.xml -r 63728 udp




# vim: set ts=4 sw=4 tw=79 ft=sh :

