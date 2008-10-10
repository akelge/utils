#!/bin/sh
# Copyright (c)2008 CUBE S.p.A. 
#  
#  Author: Andrea Mistrali <andre@cubeholding.com> 
#  Description: Fix permissions on a SVN repository
# 
#  $Id$ 
   
chgrp -R netusers *
find . -type d -exec chmod g+rwxs {} \;
find . -type f -exec chmod g+rw {} \;
