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

class mailVirtualAppDelegate(NSObject):
    accountList = IBOutlet('accountList')
    mainAddress = IBOutlet('mainAddress')
    arrayController = IBOutlet('arrayController')
    aliasTable = IBOutlet('aliasTable')
    notFound = IBOutlet('notFound')
    prefFileLabel = IBOutlet('prefFileLabel')
    modifiedIcon = IBOutlet('modifiedIcon')
    aliasList = []
    data=[]

    def awakeFromNib(self):
        # Clean up Pop Up
        self.accountList.removeAllItems()

        # Open Pref file. What if it does not exist?
        prefFile='%s/Library/Preferences/com.apple.mail.plist' % NSHomeDirectory()
        self.prefFileLabel.setStringValue_(prefFile)
        try:
            self.accounts=Accounts(filename=prefFile)
        except IOError:
            self.accounts=None

        if self.accounts:
            # Populate Pull Down
            for account in self.accounts.accountList:
                self.accountList.addItemWithTitle_(account.name)
            self.selectAccount(0)
        else:
            NSLog('No preferences found! Did you ever configured Mail.app?')
            self.notFound.setStringValue_('No accounts. Did you configured Mail.app?')
            self.prefFileLabel.setStringValue_('%s (!)' % prefFile)

        for line in os.environ['PYTHONPATH'].split(':'):
            print line
        print objc.__version__
        print objc.__path__

    def redrawArray(self):
        self.aliasList = [ NSMutableDictionary.dictionaryWithDictionary_(x) for x in self.selectedAccount.aliases ]
        self.arrayController.setContent_(self.aliasList)

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
        idx=self.arrayController.selectionIndex()
        self.selectedAccount.delAlias(idx)
        self.redrawArray()

    @IBAction
    def moveUp_(self, sender):
        self.moveUpDown(step=1)

    @IBAction
    def moveDown_(self, sender):
        self.moveUpDown(step=-1)

    def moveUpDown(self, step):
        idx=self.arrayController.selectionIndex()
        self.selectedAccount.moveAliasUpDown(idx, step)
        self.redrawArray()

    @IBAction
    def save_(self, sender):
        self.accounts.save()

    @IBAction
    def applicationWillTerminate_(self, sender):
        if self.accounts.modified:
            self.accounts.save()
