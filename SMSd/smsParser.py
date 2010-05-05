#!/usr/bin/env python
"""
Parser to transform email messages into Outgoing SMS, compatible with portechsmsd
create an alias

sms: "|/usr/local/bin/smsParser.py" [Postfix]

$Id$
"""
import email
import smtplib
import sys
import os
import re
import tempfile
from datetime import datetime
from ConfigParser import SafeConfigParser as confParser

def split160(txt):
    """
    split txt in 160 chars blocks
    """
    for i in xrange(0, len(txt), 160):
        yield txt[i:i+160]

def cleanSubject(subject):
    m=re.search('([+0-9]+)', subject)
    if m:
        return m.group()
    else:
        return None

def buildPayload(msg):
    p=msg.get_payload()
    if type(p) == list:
        # Multipart
        payload=''.join([m.get_payload() for m in p if m.get_content_type() == 'text/plain'])
    else:
        payload=p
    return split160(p)

conf=confParser()
conf.read('/etc/smsd.conf')

# Useful vars

msg = email.message_from_file(sys.stdin)
payload = buildPayload(msg)
date = datetime.now().strftime('%Y%m%d%H%M')
outDir = conf.get('smsd', 'outgoingDir')

origSubject = msg.get('Subject')
subject = cleanSubject(msg.get('Subject'))

errFrom = conf.get('email', 'from')
errTo = msg.get('From')
server = conf.get('email', 'server')

if not subject:
    errMsg = 'From: %s\n' % errFrom
    errMsg += 'To: %s\n' % errTo
    errMsg += 'Subject: Re: %s\n\n' % origSubject
    errMsg += """
Bad format of Subject in your message. Specify mobile phone number in Subject.
Oggetto del messaggio mal formato. Specificare il numero di cellulare nel Oggetto.

SMS Daemon <sms@cubeholding.com>
"""
    smtp = smtplib.SMTP(server)
    smtp.sendmail(errFrom, errTo, errMsg)
    sys.exit(0)

for pl in payload:
    fileprefix="%s_%s_" % (subject, date)
    filename=tempfile.mktemp(suffix='.txt', prefix=fileprefix, dir=outDir)
    fp=open(filename, 'w+')
    os.write(fp, pl)
    os.close(fp)
