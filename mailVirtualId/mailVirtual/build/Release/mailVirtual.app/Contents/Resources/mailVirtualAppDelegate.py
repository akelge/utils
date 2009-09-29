#
#  mailVirtualAppDelegate.py
#  mailVirtual
#
#  Created by Andrea Mistrali on 25/09/09.
#  Copyright Cube Gestioni S.r.l. 2009. All rights reserved.
#

from objc import YES, NO, IBAction, IBOutlet, pyobjc_unicode
import os
from Foundation import *
from AppKit import *
from account import *

class aliasesTable(NSObject):
    identitiesList=[]
    counter=0

    def numberOfRowsInTableView_(self, dummy):
        return self.counter

    def tableView_objectValueForTableColumn_row_(self, tableView, tableColumn, row):
        identity = self.identitiesList[row]
        identifier = tableColumn.identifier()
        return identity[identifier]

    def tableView_setObjectValue_forTableColumn_row_(self, tableView, identity, tableColumn, row):
        self.identitiesList[row][tableColumn.identifier()]=identity

    def setIdentity(self,identity,row):
        if row < len(self.identities):
            self.identitiesList[row] = identity
        else:
            self.identitiesList.append(identity)
            self.counter += 1

    def setAccount(self, account):
        self.account=account

    def setIdentities(self,ids):
        self.counter = len(ids)
        self.identitiesList = ids

    def getIdentity(self,row):
        return self.identitiesList[row]

    def getIdentities(self):
        return self.identitiesList

    def append(self,identity):
        self.counter += 1
        self.identitiesList.append(identity)

    def __len__(self):
        return self.counter

    def __getitem__(self, key):
        return self.identitiesList[key]
    
class mailVirtualAppDelegate(NSObject):
    accountList = IBOutlet('accountList')
    aliasesListTable = IBOutlet('aliasesListTable')

    def awakeFromNib(self):
        NSLog("Application did finish launching.")
        self.accounts=Accounts(filename='%s/Library/Preferences/com.apple.mail.plist'% os.environ['HOME'])
        self.accountList.removeAllItems()
        for account in self.accounts.accountList:
            self.accountList.addItemWithTitle_(account.name)
        self.selectedAccount=self.accounts.accountList[0]
        print self.selectedAccount.mainAddress
        self.populateTable_(None)

    @IBAction
    def populateTable_(self, sender):
        self.myAliasTable=aliasesTable.alloc().init()
        self.myAliasTable.setIdentities(self.selectedAccount.aliases)
        self.myAliasTable.setAccount(self.selectedAccount)
        self.aliasesListTable.setDataSource_(self.myAliasTable)

    @IBAction
    def selectAccount_(self, sender):
        print sender.title()
        idx=self.accountList.indexOfSelectedItem()
        self.selectedAccount=self.accounts.accountList[idx]
        self.populateTable_(sender)
        print self.accounts.accountList[idx]

    @IBAction
    def addAlias_(self,sender):
        self.selectedAccount.addAlias('New', 'new@domain.com')
        self.populateTable_(self)

    @IBAction
    def delAlias_(self, sender):
        idx=self.aliasesListTable.selectedRow()
        if idx > 0:
            self.selectedAccount.delAlias(idx)
            self.populateTable_(self)
        else:
            print self.myAliasTable.identities

    @IBAction
    def quit_(self, sender):
        print sender.title()
        NSQuitCommand()

    @IBAction
    def save_(self, sender):
        for item in self.selectedAccount.aliases:
            print "'%s' -> '%s'" % (item['name'], item['alias'])
        self.accounts.save()
