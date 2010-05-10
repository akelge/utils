#!/bin/bash

JAVA_HOME=/usr
GAPSLITE_HOME=.

# Do NOT modify below this line
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib:$GAPSLITE_HOME/lib/`uname -m`
export LD_LIBRARY_PATH

$JAVA_HOME/bin/java -classpath $GAPSLITE_HOME/lib/gapslite.jar:$GAPSLITE_HOME/lib/bcprov-jdk14-124.jar:$GAPSLITE_HOME/config com.grandstream.cmd.TextEncoder $*

