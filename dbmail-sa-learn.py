#!/usr/bin/env python
# -*- coding: latin-1 -*-
#  
# Copyright (c)2007 CUBE S.p.A. 
#  
#  Author: Andrea Mistrali <andre@cubeholding.com> 
#  Description: Pass all spam mail to sa-learn
# 
#  $Id$
#  $HeadURL$
#  

__version__="$Revision$"[11:-2]


"""
TODO Parsing del file di configurazione di dbmail per avere i parametri del DB
TODO Possibilità di lavorare su un'altra mailbox
"""

import sys
import getopt
import os
import MySQLdb as db


HOST="db.cube.lan"
DB="dbmail"
USER="dbmail"
PWD="dbmailpwd"
SAMBX="SpamTrain" # SA Mailbox
HAMBX="SpamNon" # Ham Mailbox
verbose=False
dryrun=False
spamOnly=False
hamOnly=False
global connection
global safd

help_message = """
This script feeds message to sa-learn, for autolearn of Spam and Ham.
Options are:
  -h|--help    show help
  -n|--dryrun  test, don't delete message
  -v|--verboes be verbose
  -H|--ham     only feed Ham
  -S|--spam    only feed Spam
 """

class Usage(Exception):
  def __init__(self, msg):
    self.msg = msg

def debug(msg):
  """print msg if verbose=True"""
  if verbose:
    print msg

 
def feedBlock(msg):
  """outputs messageblock to sa-learn if dryrun is False, else on stdout"""
  global safd
  if not dryrun:
    safd.write(msg)
  if verbose:
    print msg

def getBlocks(messageId):
  """gets all block of a message and feed them to sa-learn"""

  # Prepare the cursor to retrieve all message blocks
  messageBlockCursor=connection.cursor()
  query="""SELECT messageblk FROM dbmail_messageblks WHERE physmessage_id=%s ORDER BY messageblk_idnr""" % messageId
  messageBlockCursor.execute(query)
  for messageContent in messageBlockCursor.fetchall():
    if type(messageContent[0]) == str:
      text=messageContent[0]
    else:
      text=messageContent[0].tostring()
  return text

def getMailboxID(name=SAMBX, userID=3):
  """retrieves id of mailbox 'name' owned by user 'userID'"""
  
  global connection
  # retrieve ID of Mailbox SAMBX (SpamTraining Mailbox)
  query="SELECT mailbox_idnr FROM dbmail_mailboxes WHERE owner_idnr=%d and name='%s'" % (userID,name)
  debug(query)
  mbxid=connection.cursor()
  mbxid.execute(query)
  (mailboxId,),=mbxid.fetchall()
  debug("Working on mailbox id %d" % mailboxId)
  return mailboxId

def getMessagesList(mailboxId):
  """retrieves list of physmessage_id's of messages in mailbox"""
  
  global connection
  # Select messages from Mailbox 
  query="""SELECT physmessage_id from dbmail_messages where mailbox_idnr=%s and status < 2 ORDER by physmessage_id """ % mailboxId
  debug(query)
  messageCursor=connection.cursor()
  messageCursor.execute(query)
  return messageCursor.fetchall()

def delMessage(messageId,mailboxId):
  """set message with physmessage_id=messageId to deleted status"""
  
  global connection
  # Now we have retrieved message, let's set its status to 2.
  query="UPDATE dbmail_messages SET status=2,deleted_flag=1 WHERE physmessage_id=%s AND mailbox_idnr=%s;" % (messageId, mailboxId)
  debug(query)
  # Prepare the cursor to delete messages (setting status=2 and deleted_flag=1)
  messageDeleteCursor=connection.cursor()
  messageDeleteCursor.execute(query)
  connection.commit() # We need to commit changes!

def getWorkDone():
  """
  Select all messages from Spam Engine Train mailbox, feed them to sa-learn and mark them as deleted
  """
  global safd
  global hamOnly
  global spamOnly
  for mbx in (SAMBX, HAMBX):
    if mbx==SAMBX: # Are we working on SPAM or on HAM
      if (hamOnly):
        print "hamOnly, skipping %s" % mbx
        continue
      safd=os.popen("sa-learn --spam --mbox", 'w')
    else:
      if(spamOnly):
        print "spamOnly, skipping %s" % mbx
        continue
      safd=os.popen("sa-learn --ham --mbox", 'w')
      
    # Get mailbox ID
    mailboxId=getMailboxID(mbx)  
  
    # Process every message in mailbox
    for message in getMessagesList(mailboxId):
      # We need a "From " line at start of message
      feedBlock("From DBMAIL-EXPORTER-FOR-SA")
      text=getBlocks(message[0])
      feedBlock(text) # Feed data to sa-learn
      feedBlock("\n")
      if mbx==SAMBX:
        delMessage(message[0],mailboxId)

    if not dryrun:
      safd.close()
      
def main(argv=None):
  if argv is None:
    argv = sys.argv
  try:
    try:
      opts, args = getopt.getopt(argv[1:], "hvnHS", ["help", "verbose","dryrun", "ham", "spam"])
    except getopt.error, msg:
      raise Usage("%s\n%s" % (msg,help_message))
  
    # option processing
    for option, value in opts:
      if option in ("-S", "--spam"):
        global spamOnly
        spamOnly = True
      if option in ("-H", "--ham"):
        global hamOnly
        hamOnly = True
      if option in ("-v", "--verbose"):
        global verbose
        verbose = True
      if option in ("-n", "--dryrun"):
        global dryrun
        dryrun = True
      if option in ("-h", "--help"):
        raise Usage(help_message)
   
  except Usage, err:
    print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
    return 2
    
  # Connect to DB & open connection to sa-learn
  global connection
  connection=db.connect(db=DB,host=HOST,user=USER,passwd=PWD)
 
  getWorkDone()
  
  # Close connection to DB & to sa-learn
  connection.close()

if __name__ == "__main__":
  sys.exit(main())
