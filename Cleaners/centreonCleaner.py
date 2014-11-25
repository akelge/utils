#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""

 Copyright by Andrea Mistrali <akelge@gmail.com>
 First version: 2014-11-14T12:06 CET (+0100)

 Synopsis: Automatically mark read closed messages

 Log on to IMAP server
 Select folder
 Search for messages that:
     have X-Module: centreon
     have X-Notification: 0
     are not read yet

for each message:
    get X-Prev-Trouble-Id (pti)
    find message that has X-Trouble-Id = pti
    mark it read/delete, if exists
    mark the current message read/delete

 $Id$

"""

import imaplib
import ConfigParser
import getpass
import getopt
import sys
import os
import base64

__version__ = '1.0beta'
__author__ = 'Andrea Mistrali <andrea@e-tainment.com.mt>'


class CentreonMessage(object):
    """
    A Centreon notification message
    """

    def __init__(self, handler, uid):
        self.handler = handler
        self.uid = uid

        self._prevTroubleId = None
        self._prevTroubleMsgs = None

        # self.pti = self.prevTroubleId
        # self.pmsgs = self.prevTroubleMsgs

    def markDeleted(self):
        # if self.handler.gmail:
            # self.handler.connection.uid("store", self.uid, "+X-GM-LABLES", "\\Trash")
        # else:
            # self.handler.connection.uid("store", self.uid, "+FLAGS", "(\\Deleted)")
        self.handler.connection.uid("store", self.uid, "+FLAGS", "(\\Deleted)")

    def markUndeleted(self):
        self.handler.connection.uid("store", self.uid, "-FLAGS", "\\Deleted")

    def markRead(self):
        self.handler.connection.uid("store", self.uid, "+FLAGS", "\\Seen")

    def markUnread(self):
        self.handler.connection.uid("store", self.uid, "-FLAGS", "\\Seen")

    def moveToClosed(self):
        """
        Mark read and move to 'Closed' subfolder of the current one
        """
        self.markRead()
        if self.handler.gmail:
            # On Gmail add label for dest folder and remove label for old
            # folder
            self.handler.connection.uid("store", self.uid, "+X-GM-LABLES", "%s/Closed" % self.handler.folder)
            self.handler.connection.uid("store", self.uid, "-X-GM-LABLES", self.handler.folder)
        else:
            self.handler.connection.uid("copy", self.uid, "%s/Closed" % self.handler.folder)

    def process(self):
        if self.handler.action == "read":
            self.markRead()
        if self.handler.action == "delete":
            self.markDeleted()
        if self.handler.action == "move":
            self.moveToClosed()

    def recheck(self):
        self._prevTroubleMsgs = None

    @property
    def prevTroubleId(self):
        """
        Gets the X-Prev-Trouble-Id header
        """
        # ('OK',
            # [('39 (UID 75 BODY[HEADER.FIELDS (X-Prev-Trouble-Id)] {27}',
                # 'X-Prev-Trouble-Id: 1787\r\n\r\n'),
                # ')'])

        if self._prevTroubleId is None:
            res, payload = self.handler.connection.uid('fetch', self.uid,
                                                       '(BODY.PEEK[HEADER.FIELDS (X-prev-trouble-id)])')
            # return payload
            try:
                pti = payload[0][1]
                self._prevTroubleId = pti.split()[1]
            except:
                print "msg %s issues - payload %s " % (self.uid, payload)
        return self._prevTroubleId

    @property
    def prevTroubleMsgs(self):

        if self._prevTroubleMsgs is None:
            res, l = self.handler.connection.uid("search", None, '(HEADER X-trouble-id "%s")' %
                                                 self.prevTroubleId)
            self._prevTroubleMsgs = [CentreonMessage(self.handler, uid) for uid in
                                     l[0].split()]
        return self._prevTroubleMsgs


class CentreonMessageHandler(object):

    def __init__(self, host, username, password, folder, action, ssl=True):

        if host == 'imap.googlemail.com':
            self.gmail = True
        else:
            self.gmail = False

        if ssl is True:
            self.connection = imaplib.IMAP4_SSL(host, 993)
        else:
            self.connetion = imaplib.IMAP4(host, 143)
        self.connection.login(username, password)
        self.connection.select(folder)

        self.action = action
        self.folder = folder
        self._msgList = None

        if self.action == 'move':
            self.createClosedFolder()

    def createClosedFolder(self):
        """
        if action is "move" check if dest folder exists, else create it
        """
        res, data = self.connection.select('%s/Closed' % self.folder)
        if res == "NO":
            self.connection.create('%s/Closed' % self.folder)
        self.connection.select(self.folder)

    def recheckMsgList(self):
        self._OkMsgs = None
        return self.msgList

    @property
    def msgList(self):
        """
        Get Unseen messages from Centreon, that have Notification=0 (OK)
        """
        if self._msgList is not None:
            return self._msgList

        res, l = self.connection.uid("search", None,
                                     '(UNSEEN) (HEADER X-module "Centreon") (HEADER X-notification "0")')
        self._msgList = [CentreonMessage(self, uid) for uid in l[0].split()]

        return self._msgList

    def markRead(self, uidList):
        self.connection.uid("store", uidList, "+FLAGS", "\\Seen")
        pass

    def delete(self, uidList):
        self.connection.uid("store", uidList, "+FLAGS", "\\Deleted")
        pass

    def move(self, uidList):
        self.markRead(uidList)
        if self.gmail:
            self.connection.uid("store", uidList, '+X-GM-LABELS', "%s/Closed" % self.folder)
            self.connection.uid("store", uidList, '-X-GM-LABELS', self.folder)
        else:
            self.connection.uid("copy", uidList, "%s/Closed" % self.folder)
            self.delete(uidList)

    def processMsgs(self, uidList):
        uidList = ','.join(uidList)  # Convert into a string

        if self.action == "read":
            self.markRead(uidList)
        if self.action == "delete":
            self.delete(uidList)
        if self.action == "move":
            self.move(uidList)


def usage():
    print """
    %s [-cqh] <configfile>
     -c, --configure
     -q, --quiet
     -h, --help
     """ % os.path.basename(sys.argv[0])
    sys.exit(2)


def getInput(prompt, default='', password=False):
    line = ''

    if default != '':
        prompt = '%s [%s]: ' % (prompt, default)
    else:
        prompt = '%s: ' % (prompt)

    if password:
        while line == '':
            line = getpass.getpass(prompt)
            line = base64.b64encode(line)
    else:
        line = raw_input(prompt).strip()
        if line == '':
            line = default
    return line


def doConfigure():
    cfg = ConfigParser.SafeConfigParser()
    cfg.set('DEFAULT', 'server', getInput('IMAP Server',
            'imap.googlemail.com'))
    cfg.set('DEFAULT', 'username', getInput('Username'))
    cfg.set('DEFAULT', 'password', getInput('Password', password=True))
    cfg.set('DEFAULT', 'folder', getInput('Folder', 'INBOX'))
    action = getInput('Mark as [R]ead, [D]elete, [M]ove in "Closed" or [N]othing', 'R').upper()

    cfg.set('DEFAULT', 'action', "none")
    if action == "R":
        cfg.set('DEFAULT', 'action', "read")
    if action == "D":
        cfg.set('DEFAULT', 'action', "delete")
    if action == "M":
        cfg.set('DEFAULT', 'action', "move")

    iniFile = raw_input('File to store configuration [%s.ini]: ' %
                        getpass.getuser())
    if iniFile == '':
        iniFile = '%s.ini' % getpass.getuser()

    with open(iniFile, 'w') as f:
        cfg.write(f)

    sys.exit(0)


def parseArgs():

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hcq", ["help", "configure",
                                   "quiet"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        usage()

    verbose = True

    for o, a in opts:
        if o in ["-q", "--quiet"]:
            verbose = False

        if o in ["-c", "--configure"]:
            doConfigure()

        if o in ["-h", "--help"]:
            usage()

    if len(args) > 0:
        return verbose, args[0]
    else:
        usage()


def main():

    secondUidList = []

    verbose, cfgFile = parseArgs()
    cfg = ConfigParser.SafeConfigParser()

    if verbose:
        def debug(*args):
            print ' '.join(args)
    else:
        def debug(*args):
            pass

    try:
        with open(cfgFile) as cfgFp:
            cfg.readfp(cfgFp)
    except:
        print cfgFile, "configfile not found"
        sys.exit(3)

    action = cfg.get('DEFAULT', 'action')
    debug("Let's go")

    cmh = CentreonMessageHandler(cfg.get('DEFAULT', 'server'),
                                 cfg.get('DEFAULT', 'username'),
                                 base64.b64decode(cfg.get('DEFAULT', 'password')),
                                 cfg.get('DEFAULT', 'folder'),
                                 action)
    debug(cmh.connection.welcome)

    debug("Building unread messages list...",)
    firstUidList = [msg.uid for msg in cmh.msgList]
    debug(" %d elements in 1st level list" % len(firstUidList))

    if len(firstUidList) > 0:
        debug("Building related messages list...",)
        for msg in cmh.msgList:
            secondUidList.extend([m.uid for m in msg.prevTroubleMsgs])
        debug(" %d elements in 2nd level list" % len(secondUidList))

        cmh.processMsgs(firstUidList)

    if len(secondUidList) > 0:
        cmh.processMsgs(secondUidList)


if __name__ == "__main__":
    main()

# vim: set ts=4 sw=4 tw=79 ft=python :
