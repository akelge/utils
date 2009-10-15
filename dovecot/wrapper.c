/*
-*- coding: latin-1 -*-

 Copyright by Andrea Mistrali <am@am.cx>
 Last modified: 2009-10-15T12:01 CEST (+0200)

 Synopsis: Wrapper to another program

 $Id$


*/

#include <stdio.h>
#include <stdlib.h>
#include <libgen.h>

void usage(char *argv[]) {
    printf("Usage:\n\n");
    printf("  %s <command with fullpath> <params>\n", basename(argv[0]));
    printf("\nExec command passing params, changing UID/GID to the owner of wrapper.\n");
    printf("Remember to chown it to whom it may concern and make it suid.\n");
    exit(1);
}

int main(int argc, char *argv[]) {
    extern char **environ;

    if (argc==1) usage(argv);

    /* Change full path under */
    argv[0]="/bin/ls";

    /* Set UID/GID to the owner of executable */
    setuid(geteuid());
    setgid(getegid());
    /* Exec with environment */
    execve(argv[0], argv, environ);
    return 0;
}

