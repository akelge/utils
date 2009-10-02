#
#  mailVirtualAppDelegate.py
#  mailVirtual
#
#  Created by Andrea Mistrali on 25/09/09.
#  Copyright Cube Gestioni S.r.l. 2009. All rights reserved.
#
# $Id$

from objc import YES, NO, IBAction, IBOutlet
import objc
import os
from Foundation import *
from AppKit import *
from account import *
from arrayController import *

class mailVirtualAppDelegate(NSObject):
    accountList = IBOutlet('accountList')
    mainAddress = IBOutlet('mainAddress')
    # arrayController = IBOutlet('arrayController')
    aliasTable = IBOutlet('aliasTable')
    notFound = IBOutlet('notFound')
    prefFileLabel = IBOutlet('prefFileLabel')
    modifiedIcon = IBOutlet('modifiedIcon')
    aliasList = []

    def awakeFromNib(self):
        # Clean up Pop Up
        self.accountList.removeAllItems()

        # Open Pref file.
        # NSSearchPathForDirectoriesInDomains magic: for a complete mapping http://tinyurl.com/y9ugzou
        prefFile='%s/Preferences/com.apple.mail.plist' % NSSearchPathForDirectoriesInDomains(5,1,True)[0]
        self.prefFileLabel.setStringValue_(prefFile)

        self.accounts=Accounts(filename=prefFile)
        if self.accounts: # We have found the prefFile
            # Populate Pull Down
            for account in self.accounts.accountList:
                self.accountList.addItemWithTitle_(account.name)
            self.selectAccount(0)
        else: # Pref file does not exist
            NSLog('No preferences found! Did you ever configured Mail.app?')
            self.notFound.setStringValue_('No accounts. Did you configured Mail.app?')
            self.prefFileLabel.setStringValue_('%s (!)' % prefFile)

    def redrawArray(self):
        self.aC=arrayController.alloc().init()
        self.aC.setIdentities(self.selectedAccount.aliases)
        self.aliasTable.setDataSource_(self.aC)

    def selectAccount(self, idx):
        self.selectedAccount=self.accounts.accountList[idx]
        self.mainAddress.setStringValue_(self.selectedAccount.mainAddress)
        self.redrawArray()

    @IBAction
    def selectAccount_(self, sender):
        idx=self.accountList.indexOfSelectedItem()
        self.selectAccount(idx)
        self.redrawArray()

    @IBAction
    def addAlias_(self,sender):
        self.selectedAccount.addAlias('New', 'new@domain.com')
        self.redrawArray()

    @IBAction
    def delAlias_(self, sender):
        idx=self.aliasTable.selectedRow()
        self.selectedAccount.delAlias(idx)
        self.redrawArray()

    @IBAction
    def moveUp_(self, sender):
        self.moveUpDown(step=1)

    @IBAction
    def moveDown_(self, sender):
        self.moveUpDown(step=-1)

    def moveUpDown(self, step):
        idx=self.aliasTable.selectedRow()
        self.selectedAccount.moveAliasUpDown(idx, step)
        self.redrawArray()
        self.aliasTable.selectRowIndexes_byExtendingSelection_(NSIndexSet.indexSetWithIndex_(idx-step), NO)
        

    @IBAction
    def save_(self, sender):
        self.accounts.save()

    @IBAction
    def applicationWillTerminate_(self, sender):
        if self.accounts.modified:
            self.accounts.save()
