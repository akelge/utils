#!/bin/sh
# -*- coding: latin-1 -*-

# Copyright by Andrea Mistrali <am@am.cx>
# First version: 2010-03-18T13:54 CET (+0100)
#
# Synopsis: Install CFG on PBX
#
# $Id$
scp -P 222 generateConfigResults/cfg* root@pbx.voip:/tftpboot/
