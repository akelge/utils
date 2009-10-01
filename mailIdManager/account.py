#
#  account.py
#  mailVirtual
#
#  Created by Andrea Mistrali on 25/09/09.
#  Copyright (c) 2009 Cube2 Gestioni S.r.l.. All rights reserved.
#
# $Id$

import plistlib
from os import system
import sys
from xml.parsers.expat import ExpatError

class Accounts:
    def __init__(self, filename="com.apple.mail.plist"):
        self.filename=filename
        self.modified=False
        self.binary=False
        self.accountList=[]
        # Open PL
        try:
            self.pl=plistlib.readPlist(self.filename)
        except ExpatError:
            system('plutil -convert xml1 %s' % self.filename)
            self.binary=True
            self.pl=plistlib.readPlist(self.filename)

        accountList=[a for a in self.pl['MailAccounts'] if (a['AccountType'] in ['IMAPAccount', 'POPAccount'])]
        for account in accountList:
            self.accountList.append(Account(account, self))

    def save(self, filename=None):
        if not filename:
            filename=self.filename

        # save in XML
        plistlib.writePlist(self.pl, filename)
        # Convert to binary if necessary
        if self.binary:
            system('plutil -convert binary1 %s' % filename)
        self.modified=False

class Account:
    def __init__(self, accountDict, parent):
        self.account=accountDict
        self.name=self.account['AccountName']
        self.parent=parent
        self.mainAddress = "%s <%s>" % (self.account['FullUserName'], self.account['EmailAddresses'][0])

        # Setup Aliases
        if not self.account.has_key('EmailAliases'):
            self.account['EmailAliases']=[]
        self.aliases=self.account['EmailAliases']

    def __repr__(self):
        return r"<Account '%s'>" % (self.name)

    def addAlias(self, name, alias, index=None):
        newAlias={'name': name, 'alias': alias}
        if index != None:
            self.aliases.insert(index, newAlias)
        else:
            self.aliases.append(newAlias)
        self.parent.modified=True

    def delAlias(self, index):
        if index in range(0,len(self.aliases)):
            self.aliases.pop(index)
            self.parent.modified=True

    def modAlias(self, index, name, alias):
        if index in range(0,len(self.aliases)):
            self.delAlias(index)
            self.addAlias(name, alias, index)
            self.parent.modified=True

    def moveAliasUpDown(self, index, step):
        """
        Move an alias of step positions in list, watching for overflow
        """
        if (index-step) in range(0,len(self.aliases)):
            item=self.aliases.pop(index)
            self.aliases.insert((index-step), item)
            self.parent.modified=True
