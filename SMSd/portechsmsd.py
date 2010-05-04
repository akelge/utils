#!/usr/bin/env python
#-*- coding: latin-1 -*-

import smtplib, hashlib, re, datetime, os, time, sys
import logging
import signal
from telnetlib import Telnet
from ConfigParser import SafeConfigParser as confParser

__author__ = 'Andrea Mistrali <am@cubeholding.com>'

"""
Docs from
    http://www.developershome.com/sms/

Message from list
+CMGL: 50,"REC READ","+393391381048",,"10/03/19,11:53:25+04"
Ho chiamato alle 11:53 del 19/03/10. Informazione gratuita del servizio CHIAMAMI di Vodafone.

Message from get
+CMGR: "REC READ","+85291234567",,"07/02/18,00:12:05+32"
Hello, welcome to our SMS tutorial.

TODO
Encode/decode of ISO-8859-1
"""

DEFAULTS= {
        'processname': 'portechsmsd',
        'pidfile': '/var/run/smsd.pid',
        'logfile': '/var/log/smsd.log',
        'loglevel': 'INFO',
        'timeout': '10'
            }

class OutMsg(object):
    """
    Class for outgoing messages
    filename format is "phNumber_date_uniquetext.txt"
    phNumber MUST be in format +<INTPREFIX><NUMBER> or simply <NUMBER>
    so

    +3934661xxxx_20100503_unique1.txt is valid
    346610xxxx_20100503_unique1.txt is valid too

    and they will go to the same Cell phone
    """

    def __init__(self, filename=None, phNumber=None, text=None, smsgw=None):
        self.good=False
        self.smsgw=smsgw
        if filename:
            self.filename=filename
            (self.phNumber, date, uniqText) = os.path.basename(filename).split('_')
            (uniqText, ext) = uniqText.split('.')

            self.text=open(filename, 'r+').read()

        else:
            self.filename=None
            self.smsgw=smsgw
            self.text=text.decode('utf-8')
            self.phNumber='+%s' % phNumber

        if self.text and self.phNumber and self.smsgw:
            self.good=True

    def __repr__(self):
        return r"<%s(phNumber=%s)>" % (self.__class__.__name__, self.phNumber)

    def __str__(self):
        return u"to %s\n%s" % (self.phNumber, self.text)

    def send(self):
        if self.good:
            self.smsgw.debug('Sending message to %s' % self.phNumber)
            self.smsgw.openModule1()
            self.smsgw.sendCmd('AT+CMGS="%s"\r%s%c' % (self.phNumber, self.text, 26)) # chr(26) = Ctrl-Z
            self.smsgw.closeModule1()

    def delete(self):
        if self.good and self.filename:
            self.smsgw.debug('Deleting file %s' % self.filename)
            os.unlink(self.filename)

class InMsg(object):
    """
    Incoming message
    When saved filename would be phNumber_date_md5.txt
    We use md5 to be sure that filename for a message is unique, but if we save twice the same message
    no file duplication will happen.
    """

    def __init__(self, data, msg, index=None, smsgw=None):
        """
        data: +CMGL: 50,"REC READ","+393391381048",,"10/03/19,11:53:25+04"
        msg: Ho chiamato alle 11:53 del 19/03/10. Informazione gratuita del servizio CHIAMAMI di Vodafone.

        data: +CMGR: "REC READ","+85291234567",,"07/02/18,00:12:05+32"
        msg: Hello, welcome to our SMS tutorial.

        """
        self.good=False
        self.data=data.strip()
        self.text=msg.strip()
        self.index=index
        self.smsgw=smsgw
        self.parse()

    def parse(self):
        try:
            (self.cmd, data)=self.data.split(': ')
        except ValueError:
            self.smsgw.error("Error parsing message: data: %s - msg: %s" % (data, msg))
            return

        self.cmd=self.cmd.strip()

        if self.cmd == "+CMGL": # Got message from list command
            (self.index, status, phNumber, dummy, date, time) = data.split(',')
            self.index=int(self.index)

        elif self.cmd == "+CMGR": # Got message from retr command, we have index
            (status, phNumber, dummy, date, time) = data.split(',')
            self.index=index

        else:
            self.smsgw.error("Invalid command %s - data: %s - msg: %s" % (self.cmd, self.data, self.msg))
            return

        self.status=status.replace('"', '')
        self.phNumber=phNumber.replace('"', '')
        self.date="20%sT%s" % (date.replace('/', '-'), time) # Canonical ISO format, we assume that year >= 2000
        self.date=self.date.replace('"', '')
        self.date=datetime.datetime.strptime('-'.join(self.date.split('+')[0].split('-')[0:3]), '%Y-%m-%dT%H:%M:%S')
        self.good=True

    def __repr__(self):
        return r"<%s(index=%02d, status='%s', phNumber=%s, date=%s)>" % (self.__class__.__name__,
                self.index,
                self.status,
                self.phNumber,
                self.date)

    def __str__(self):
        return u"[%02d] from %s on %s [%s]\n%s" % (self.index,
                self.phNumber,
                self.date,
                self.status,
                self.text)

    def msgTxt(self):
        return 'Date: %s\nFrom: %s\n\n%s' % (self.date, self.phNumber, self.text)

    def save(self):
        """
        save message in a file
        """
        if self.good:
            filename='%s/%s_%s_%s.txt' % (self.smsgw.c.get('smsd', 'savedDir'),
                    self.phNumber,
                    self.date.strftime('%Y%m%d%H%M%S'),
                    hashlib.md5(self.text).hexdigest())

            open(filename, 'w+').write(self.msgTxt)

    def send(self):
        """
        Send message by mail
        """
        if self.good:
            sender = self.smsgw.sender
            to = self.smsgw.to
            server = self.smsgw.server

            self.smsgw.debug('sending message to %s' % to)
            msg  = 'From: %s\n' % sender
            msg += 'To: %s\n' % to
            msg += 'Subject: Short message from %s\n\n' % (self.phNumber)
            msg += self.msgTxt()
            smtp=smtplib.SMTP(server)
            smtp.sendmail(sender, to, msg)

    def delete(self):
        if self.good:
            self.smsgw.debug('Deleting SMS %d' % self.index)
            self.smsgw.delete(self.index)


class SMSgw(object):
    """
    Interface to Portech
    """
    def __init__(self, conf=None, logger=None):
        """
        self.t -> telnet to host
        self.c -> configuration from ini file
        """
        if not conf:
            conf=confParser()
            conf.read(['/etc/smsd.conf', 'smsd.conf'])
        self.c=conf
        self.setConf()
        if not logger:
            self.initLog()
        else:
            self.logger=logger

    def setConf(self):
        # Telnet params
        self.hostname=self.c.get('network', 'hostname')
        self.username=self.c.get('network', 'username')
        self.password=self.c.get('network', 'password')
        self.timeout=self.c.getfloat('network', 'timeout')
        # Email params
        self.sender = self.c.get('email', 'from')
        self.to = self.c.get('email', 'to')
        self.server = self.c.get('email', 'server')

        self.ok=re.compile('0\r\n')
        self.polling=True
        self.inMsgs=[]
        self.outMsgs=[]

    def initLog(self):
        self.logger=logging.getLogger('smsd')
        smsLogHandler=logging.StreamHandler()
        smsLogHandler.setLevel(logging.DEBUG)
        smsLogFormatter=logging.Formatter("%(levelname)s: %(message)s")
        smsLogHandler.setFormatter(smsLogFormatter)
        self.logger.addHandler(smsLogHandler)
        self.logger.setLevel(logging.DEBUG)

    # Commodity wrappers
    def debug(self, msg): return self.logger.debug(msg)
    def info(self, msg): return self.logger.info(msg)
    def error(self, msg): return self.logger.error(msg)


    def connect(self):
        self.t=Telnet(self.hostname, 23)
        self.t.set_debuglevel(0)
        self.t.read_until('username:', self.timeout)
        self.t.write('%s\r\n' % self.username)
        self.t.write('%s\r\n' % self.password)
        self.t.read_until(']', self.timeout)
        self.info("connected to %s" % self.hostname)

    def logout(self):
        self.sendCmd('logout', 'exit...')
        self.t.close()
        del self.t
        self.info("logout from %s" % self.hostname)

    # Low level device communication commands
    def sendCmd(self, cmd, expectStr=None):
        if not expectStr:
            expectStr=self.ok
        self.t.write('%s\r\n' % cmd)
        res=self.t.expect([expectStr], self.timeout)
        return res[2]

    def openModule1(self):
        self.debug('open module1')
        self.sendCmd('module1', 'release module 1')
        self.sendCmd('ate0')
        self.sendCmd('atv0')
        self.sendCmd('at+cmgf=1')

    def closeModule1(self):
        self.debug('close module1')
        self.sendCmd(chr(24), 'release module 1') # chr(24) = Ctrl-X

    # MSGS management commands
    def poll(self):
        self.pollIn()
        self.pollOut()

    def pollIn(self, status="ALL"):
        self.debug('polling incoming messages...')
        self.inMsgs=[]
        self.openModule1()
        msgList=self.sendCmd('AT+CMGL="%s"' % status)
        self.closeModule1()
        msgs=msgList.split('\r\n')
        # cleanup
        for count in range(msgs.count('')): msgs.remove('')

        for idx in range(0,len(msgs),2):
            try:
                self.inMsgs.append(InMsg(msgs[idx], msgs[idx+1], smsgw=self))
            except:
                pass
        self.debug('Got %d incoming messages' % len(self.inMsgs))

    def pollOut(self):
        self.debug('polling outgoing messages...')
        self.outMsgs=[]
        pollDir=self.c.get('smsd', 'outgoingDir')
        for f in os.listdir(pollDir):
            self.outMsgs.append(OutMsg(filename='%s/%s' % (pollDir, f), smsgw=self))
        self.debug('Got %d outgoing messages' % len(self.outMsgs))


    def count(self):
        return len(self.inMsgs)

    def retr(self, idx):
        if idx <= self.count():
            return self.inMsgs[idx]
        else:
            return None

    def delete(self, idx):
        self.openModule1()
        self.sendCmd('AT+CMGD=%d' % idx)
        self.closeModule1()
        msg=[m for m in self.inMsgs if m.index==idx][0]
        self.inMsgs.pop(self.inMsgs.index(msg))

    # MSGS I/O commands
    def saveAll(self):
        self.debug('Saving all messages')
        for msg in self.inMsgs: msg.save()

    def sendAll(self):
        for msg in self.inMsgs:
            msg.send()
            msg.delete()
        for msg in self.outMsgs:
            msg.send()
            msg.delete()


class SMSd(object):

    def __init__(self, autostart=True):
        self.parseConf()
        self.initLog()
        # Fork
        if autostart:
            pid = os.fork()
            if pid:
                # Parent
                sys.exit(0)
            else:
                # Child
                self.setProcessName()
                self.smsgw=SMSgw(conf=self.c, logger=self.logger)
                self.writePID()
                self.setupSignals()
                self.idleCycle()


    def parseConf(self):
        self.c = confParser(DEFAULTS)
        self.c.read(['/etc/smsd.conf', 'smsd.conf'])
        self.pidfile = self.c.get('smsd', 'pidfile')
        self.logfile = self.c.get('smsd', 'logfile')
        self.loglevel = self.c.get('smsd', 'loglevel')

    def setProcessName(self):
        # change process name
        try:
            import procname
            procname.setprocname(self.c.get('smsd', 'processname'))
            self.debug("set process name to '%s'" % self.c.get('smsd', 'processname'))
        except:
            self.error('no procname module found, not setting process name...')

    def initLog(self):
        # Set up logging
        self.logger=logging.getLogger('smsd')

        smsLogHandler=logging.FileHandler(self.logfile)
        smsLogHandler.setLevel(getattr(logging, self.loglevel))

        smsLogFormatter=logging.Formatter("%(asctime)s %(name)s[%(process)d] %(levelname)s: %(message)s", datefmt='%Y-%m-%dT%H:%M')
        smsLogHandler.setFormatter(smsLogFormatter)

        self.logger.addHandler(smsLogHandler)
        self.logger.setLevel(getattr(logging, self.loglevel))

    def debug(self, msg): return self.logger.debug(msg)
    def info(self, msg): return self.logger.info(msg)
    def error(self, msg): return self.logger.error(msg)

    def writePID(self):
        open(self.pidfile, 'w').write('%d\n' % os.getpid())

    def setupSignals(self):
        signal.signal(signal.SIGUSR1, signal.SIG_IGN)
        signal.signal(signal.SIGUSR2, signal.SIG_IGN)
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, self.exit)

    def idleCycle(self):
        pollCount=0
        self.smsgw.connect()
        while True:
            self.smsgw.poll()
            self.smsgw.sendAll()
            time.sleep(60)
            pollCount+=1
            if pollCount==10:
                self.info('Max polls reached, relogin...')
                self.smsgw.logout()
                time.sleep(20)
                self.smsgw.connect()
                pollCount=0

    # Signal handlers
    def exit(self, signal, param):
        self.info('Got TERM signal, exiting...')
        self.smsgw.logout()
        os.unlink(self.pidfile)
        self.info('Bye bye')
        exit(0)

# Main
if __name__ == '__main__':
    s=SMSd()
