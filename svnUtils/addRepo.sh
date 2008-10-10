#!/bin/sh
# Copyright (c)2008 CUBE S.p.A. 
#  
#  Author: Andrea Mistrali <andre@cubeholding.com> 
#  Description: Create a new svn repository, fix permissions and create standard structure
# 
#  $Id$ 

if [ $# -lt 1 ]; then
  echo Syntax: `basename $0` "<repositoryName>"
  exit 2
fi

mkdir $1
svnadmin create $1
chgrp -R netusers $1
find $1 -type d -exec chmod g+rwxs {} \;
find $1 -type f -exec chmod g+rw {} \;

NEWREPO="`pwd`/$1"
cd /tmp

svn co file://${NEWREPO}
cd $1 
mkdir branches tags trunk 
svn add *
svn commit -m "Startup structure"

cd /tmp
rm -rf $1
