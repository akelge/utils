#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c)2008 CUBE S.p.A.
#
#  Author: Andrea Mistrali <andre@cubeholding.com>
#  Description: Scarica cambi da UIC e aggiorna DB
#
#  $Id$
#  $HeadURL$

# http://uif.bancaditalia.it/UICFEWebroot/QueryOneDateAllCur?lang=ita&rate=0&init
# Day=07&initMonth=01&initYear=2008&refCur=euro&R1=csv


import psycopg2 as db
import time
import datetime
import urllib2
import csv
import getopt
import sys

__version__ = "$Revision$"[11:-2]

currency = {'USD': 2, 'GBP': 3}
baseUrl = "http://uif.bancaditalia.it/UICFEWebroot/QueryOneDateAllCur?lang=ita&rate=0&initDay=%02d&initMonth=%02d&initYear=%4d&refCur=%s&R1=csv"
OUTFILE = "/tmp/%snewUic%s.csv"

DB = "gv"
HOST = "localhost"
USER = "root"
PWD = "chpwd"

DSN = "dbname=%s user=%s password=%s host=%s" % (DB, USER, PWD, HOST)


def usage():
    print """
    %s [-n|--nofile] [-f|--nodb] -d|--date "data" - Scarica i cambi di un solo giorno. Per default ieri.
    %s [-n|--nofile] [-f|--nodb] -s|--start "dataInizio" [-e|--end "dataFine"] - Scarica i cambi a partire da dataInizio, fino a dataFine. dataFine è, per default, ieri.

    Il flag -n fa si che i dati non vengano salvati in un file.
    Il flag -f fa si che i dati non vengano inseriti nel DB.

    Tutte le date vanno indicate nel formato "dd/mm/yyyy".
    """ % (sys.argv[0], sys.argv[0])


def download(date, writeFile=True):
    """
    Scarica il file relativo ad una certa data e rende il file parserato
    date è un array [dd,mm,yyyy]
    """
    EURurl = baseUrl % (date[0], date[1], date[2], 'euro')
    USDurl = baseUrl % (date[0], date[1], date[2], 'dollari')
    strDate = "%d%02d%02d" % (date[2], date[1], date[0])

    print "Scarico da %s" % EURurl
    f = urllib2.urlopen(EURurl)
    t = f.readlines()
    if writeFile:
        out = open(OUTFILE % ('EUR', strDate), 'w')
        out.write(''.join(t))
        out.close()
    reader = csv.reader(t)

# Hack per prelevare anche i cambi in Dollari
    if writeFile:
        print "Scarico da %s" % USDurl
        f = urllib2.urlopen(USDurl)
        out = open(OUTFILE % ('USD', strDate), 'w')
        out.write(''.join(f.readlines()))
        out.close()
    return reader


def insertOrUpdate(date, cod1, cod2, cambio):
    dataDict = {'date': date,
                'cod1': cod1,
                'cod2': cod2,
                'cambio': cambio}

    selQuery = """SELECT cod_cambio FROM cambio_new where data_cambio='%(date)s' and
    ((cod_cambio1=%(cod1)d and cod_cambio2=%(cod2)d) or
    (cod_cambio1=%(cod2)d and cod_cambio2=%(cod1)d))""" % dataDict

    insQuery = """INSERT INTO cambio_new (data_cambio, cod_cambio1, cod_cambio2, cambio)
    VALUES ('%(date)s', %(cod1)d, %(cod2)d, %(cambio).5f)""" % dataDict

    updQuery = """UPDATE cambio_new SET cambio=%(cambio).5f WHERE
    cod_cambio1=%(cod1)d AND
    cod_cambio2=%(cod2)d AND
    data_cambio='%(date)s'""" % dataDict

    # Connettiamoci al DB
    connection = db.connect(DSN)
    cursor = connection.cursor()
    cursor.execute(selQuery)

    if not len(cursor.fetchall()):
        cursor.execute(insQuery)
    else:
        cursor.execute(updQuery)
    connection.commit()


def main():
    done = False
    writeFile = True
    dbInsert = True
    oneDay = datetime.timedelta(1)

    startDate = 0
    endDate = 0
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:e:nfs:", [
                                   "date=", "nofile", "nodb", "start=", "end="])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o == "-n":
            writeFile = False
        if o == '-f':
            dbInsert = False
        if o == "-h":
            usage()
            sys.exit(2)
        if o == "-d":
            date = a
            dateArray = map(int, date.split('/'))
            startDate = datetime.date(dateArray[2], dateArray[1], dateArray[0])
            endDate = startDate
        if o == "-s":
            date = a
            dateArray = map(int, date.split('/'))
            startDate = datetime.date(dateArray[2], dateArray[1], dateArray[0])
        if o == "-e":
            date = a
            dateArray = map(int, date.split('/'))
            endDate = datetime.date(dateArray[2], dateArray[1], dateArray[0])

            if endDate and not startDate:
                usage()
                sys.exit(2)

    date = time.strftime("%d/%m/%Y", time.gmtime(time.time() - 86400))  # Ieri
    dateArray = map(int, date.split('/'))

    if not startDate:
        startDate = datetime.date(dateArray[2], dateArray[1], dateArray[0])

    if not endDate:
        endDate = datetime.date(dateArray[2], dateArray[1], dateArray[0])

    while startDate <= endDate:
        print "Scarico i dati del %02d/%02d/%4d" % (startDate.day, startDate.month, startDate.year)
        done = False
        # if writeFile:
            # strDate = "%d%02d%02d" % (startDate.year, startDate.month, startDate.day)

        dateArray = [startDate.day, startDate.month, startDate.year]
        reader = download(map(int, dateArray), writeFile=writeFile)
        dbDate = "%04d-%02d-%02d" % (dateArray[2], dateArray[1], dateArray[0])
        for l in reader:
            if len(l) > 1:
                done = True
                if l[2] in currency.keys() and dbInsert:
                    insertOrUpdate(dbDate, 1, currency[l[2]], float(l[4]))
        if done and dbInsert:
            # Inseriamo i cambi fissi
            insertOrUpdate(dbDate, 1, 1, 1)
            insertOrUpdate(dbDate, 2, 2, 1)
            insertOrUpdate(dbDate, 3, 3, 1)

        startDate = startDate + oneDay


if __name__ == "__main__":
    main()
