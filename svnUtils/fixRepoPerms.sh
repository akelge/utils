#!/bin/sh
chgrp -R netusers *
find . -type d -exec chmod g+rwxs {} \;
find . -type f -exec chmod g+rw {} \;
