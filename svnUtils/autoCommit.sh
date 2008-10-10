#!/bin/sh
# -*- coding: latin-1 -*-
# Copyright (c)2008 CUBE S.p.A. 
#  
#  Author: Andrea Mistrali <andre@cubeholding.com> 
#  Description: Auto Commit
# 
#  $Id$ 

function autoAddDel {
    svn status | grep '^?' | sed -e 's/^?      /svn add "/g' -e 's/$/"/g'
    svn status | grep '^!' | sed -e 's/^!      /svn delete "/g' -e 's/$/"/g'
    msg="Autocommit - `date +%Y%m%d%H%M` $LOGNAME"
    echo 'svn commit -m "Autocommit - `date +%Y%m%d%H%M` $LOGNAME"'
}

if [ "$1" == "-h" ]; then
    cat<<EOF
`basename $0` [-hni]
   -h show help
   -n dryrun
   -i interactive: ask confirmation
EOF
    exit 2
fi

if [ "$1" == "-n" ]; then
    autoAddDel
elif [ "$1" == "-i" ]; then
    echo "Operations:"
    autoAddDel
    echo -n "Confirm [y/n]? "
    read answer
    if [ $answer == 'y' ] || [ $answer == 'Y' ]; then
        autoAddDel | sh
    fi
else
    autoAddDel | sh
fi
