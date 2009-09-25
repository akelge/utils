#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""

 Copyright by Andrea Mistrali <am@am.cx>
 First version: 2009-09-25T13:07 CEST (+0200)
 Last modified: 2009-09-25T13:18 CEST (+0200)

 Synopsis: Mail.app Virtual Identities Manager

 $Id$

This file is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2, or (at your option)
any later version.
This file is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

"""

__version__ ='1.0'
__author__ ='Andrea Mistrali <am@am.cx>'

import plistlib
from os import system
import sys
from xml.parsers.expat import ExpatError

class Account:
    """
    Class to manage Mail.app accounts
    """
    def __init__(self, name='com.apple.mail.plist'):
        self.name=name
        self.binary=False # plist format
        self.modified=False

        # Open PL
        try:
            self.pl=plistlib.readPlist(self.name)

        except IOError:
            print "ERROR: No such file: %s\n" % self.name
            sys.exit(1)

        except ExpatError:
            system('plutil -convert xml1 %s' % self.name)
            self.binary=True
            self.pl=plistlib.readPlist(self.name)

        print " > Loaded %s (binary: %s)" % (self.name, self.binary)
        # Choose account
        accountList=[a for a in self.pl['MailAccounts'] if a['AccountType'] in ['IMAPAccount', 'POPAccount']]
        print " > Making account choice\n"
        print "Id Name"
        print "-" * 7
        for a in accountList:
            print "%2d %-20s" % (accountList.index(a),a['AccountName'])
        print
        choice=-1
        while choice not in map(str,range(0,len(accountList)-1)):
            choice=raw_input('Id [0-%d]> ' % (len(accountList)-1))
        self.accountIndex=int(choice)
        self.account=accountList[self.accountIndex]
        self.accountName = self.account['AccountName']

        # Setup Aliases
        if not self.account.has_key('EmailAliases'):
            self.account['EmailAliases']=[]
        self.aliases=self.account['EmailAliases']

    def __repr__(self):
        return r"<Account '%s' from '%s'>" % (self.account['AccountName'], self.name)

    def listAliases(self):
        """
        Show formatted list of Aliases found
        """
        print "\n%2s %-20s %20s" % ('Id', 'Name', 'Address')
        print '-' * 44
        for item in self.aliases:
            print "%2d %-20s %20s" % (self.aliases.index(item), item['name'], item['alias'])
        print

    def addAlias(self):
        """
        Add alias to list
        """

        name=raw_input('Real Name: ')
        alias=raw_input('Address: ')
        self.aliases.append({'name': name, 'alias': alias})
        self.modified=True

    def chooseAlias(self):
        """
        Choose alias to delete/modify
        """
        choice=-1
        while choice not in map(str,range(0,len(self.aliases)))+['-']:
            choice=raw_input('Address Id [0-%d, -]: ' % (len(self.aliases)-1))
        if choice=='-':
            return
        return choice

    def delAlias(self):
        """
        Delete alias from list
        """
        choice=self.chooseAlias()
        self.aliases.pop(int(choice))
        self.modified=True

    def save(self):
        """
        Save file in correct (original) format
        """
        plistlib.writePlist(self.pl, self.name)
        if self.binary:
            system('plutil -convert binary1 %s' % self.name)
        print "Saved in %s (binary: %s)" % (self.name, self.binary)
        self.modified=False

    def quit(self):
        """
        Exit from program, asking to save if necessary
        """
        if self.modified:
            choice=''
            while choice.upper() not in ['Y','N','S']:
                choice=raw_input("List of addresses changed. Quit anyway [Yes/No/Save&Quit]? ")
            if choice.upper() == 'N':
                self.choose()
            if choice.upper() == 'S':
                self.save()
        print "\nThanks for flying with us. Bye!"
        sys.exit(0)

    def printLegend(self):
        """
        Print legend of commands
        """
        print "A)dd\nD)el\nL)ist\nS)ave\nQ)uit"

    def choose(self):
        """
        Choose what to do
        """
        choice=''
        while choice.upper() not in ['A','D','L','S','Q','?']:
            choice=raw_input('[%s] A/D/L/S/Q/?> ' % self.accountName)

        if choice.upper() == 'A':
            self.addAlias()
            self.choose()

        if choice.upper() == 'D':
            self.delAlias()
            self.choose()

        if choice.upper() == 'L':
            self.listAliases()
            self.choose()

        if choice.upper() == 'S':
            self.save()
            self.choose()

        if choice.upper() == 'Q':
            self.quit()

        if choice.upper() == '?':
            self.printLegend()
            self.choose()


print "\nThe Mail.app Virtual Identities Manager"
print "---------------------------------------\n"

name="com.apple.mail.plist"
if len(sys.argv) > 1:
    name=sys.argv[1]

account=Account(name=name)
account.listAliases()
account.choose()
