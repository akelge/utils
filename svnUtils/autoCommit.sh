#!/bin/sh
# -*- coding: latin-1 -*-
# Copyright (c)2008 CUBE S.p.A. 
#  
#  Author: Andrea Mistrali <andre@cubeholding.com> 
#  Description: Auto Commit
# 
#  $Id$ 

function autoAddDel {
    svn status 2>/dev/null| grep '^?' | sed -e 's/^?      /svn add "/g' -e 's/$/"/g'
    svn status 2>/dev/null| grep '^!' | sed -e 's/^!      /svn delete "/g' -e 's/$/"/g'
    msg="Autocommit - `date +%Y%m%d%H%M` $LOGNAME"
    cat<<EOB
svn commit -m "Autocommit - `date +%Y%m%d%H%M` $LOGNAME $message"
EOB
}

if [ '$1' == '-h' ]; then
    cat<<EOF
`basename $0` [-hni] message
   -h show help
   -n dryrun
   -i interactive: ask confirmation
   message Commit message
EOF
    exit 2
fi
dryrun=0
ask=0

for arg in $*; do
    if [ "$arg" == '-n' ]; then
        dryrun=1
        shift
    elif [ "$arg" == '-i' ]; then
        ask=1
        shift
    else
        message=$*
    fi
done

if [ $dryrun -eq 1 ]; then
    autoAddDel
elif [ $ask -eq 1 ]; then
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
