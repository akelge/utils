/*
-*- coding: latin-1 -*-

 Copyright by Andrea Mistrali <am@am.cx>
 Last modified: 2009-10-15T11:04 CEST (+0200)

 Synopsis: Wrapper to another program

 $Id$


*/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    extern char **environ;
    int n;
    argv=argv++;
    for(n=0; n<argc-1; n++)
        printf("%s\n", argv[n]);
    for(n=0; n < sizeof(environ); n++)
        printf("%s\n", environ[n]);
    setuid(geteuid());
    setgid(getegid());
    execve(argv[0], argv, environ);
    return 0;
}

