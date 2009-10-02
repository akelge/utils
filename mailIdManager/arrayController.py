from Foundation import *
from objc import YES, NO

class arrayController(NSArrayController):
    identitiesList=[]
    counter=0

    def init(self):
        super(arrayController, self).init()
        self.setPreservesSelection_(YES)
        self.setAvoidsEmptySelection_(YES)
        self.setAutomaticallyRearrangesObjects_(YES)
        return self
 
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


