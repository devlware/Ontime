#!/usr/bin/python
# coding: utf-8
# 
# ontime
#
# Software to download the schedule for all public bus lines in Curitiba.
# Please do *NOT* use it for illegal purposes.
#
# Patches & fixes: Diego W. Antunes <devlware@gmail.com>

import urllib2
from urllib2 import Request, urlopen, URLError, HTTPError
import tempfile
import random
import thread, time
import threading
import string
import sqlite3
import getopt, sys
import os
from os.path import join, getsize
import hashlib
import datetime

__version__ = "1.0"
__author__ = 'Diego W. Antunes'
__license__ = 'Maybe MIT'


CAPURL = 'http://www.urbs.curitiba.pr.gov.br/PORTAL/tabelahorario/cap.php'

class CaptchaException(Exception):
    """Captcha exception."""

class IMBDataBase():
    """ """

    def __init__(self, database = None):
        """ """
        self.data = []
        self.conn = None
        self.cur = None
        self.setDatabase(database)
        self.connectDB()

    def setDatabase(self, database):
        """ Sets the database used to store the captcha image file. """
        if len(database) > 4:
            self.database = database
        else:
            print('Database name < 4')

    def connectDB(self):
        """ """
        self.conn = sqlite3.connect(self.database)
        self.cur = self.conn.cursor()

        try:
            self.cur.execute('CREATE TABLE CaptchaSha1 (pk INTEGER PRIMARY KEY NOT NULL, fn TEXT, shasum TEXT, size INTEGER, occurrences INTEGER)')
        except sqlite3.OperationalError, msg:
            print msg

    def createDB(self):
        """ """
        print "running..."

        try:
            # Create table
            self.cur.execute('CREATE TABLE CaptchaSha1 (pk INTEGER PRIMARY KEY NOT NULL, fn TEXT, shasum TEXT, size INTEGER, occurrences INTEGER)')
        except sqlite3.Error, e:
            print "An error occurred:", e.args[0]
            print "Problems in db creation"
            return 0

        # Save (commit) the changes
        try:
            self.conn.commit()
            print "Banco criado com sucesso"
#            self.cur.close()
        except sqlite3.Error, e:
            print "An error occurred:", e.args[0]
        
    def saveData(self, fn, sha, size):
        """ """

 #       cur = self.conn_.cursor()
        try:
            self.cur.execute('SELECT pk, occurrences FROM CaptchaSha1 WHERE shasum = ?', (sha, ))
            row = self.cur.fetchone()
            
            if row:
                pk = row[0]
                occ = row[1]
                try:
                    aTuple = (occ+1, pk, )
                    self.cur.execute('UPDATE CaptchaSha1 SET occurrences = ? WHERE pk = ?', aTuple)
                    self.conn.commit()
                except sqlite3.Error, e:
                    print "An error occurred:", e.args[0]
            else:
                # Insert a row of data
                t = (fn, sha, size, 1)
                try:
                    self.cur.execute('INSERT INTO CaptchaSha1 (fn, shasum, size, occurrences) values (?, ?, ?, ?)', t)
                    self.conn.commit()
                except sqlite3.Error, e:
                    print "An error occurred:", e.args[0]

        except sqlite3.Error, e:
            print "An error occurred:", e.args[0]
            return 0

    def closeDB(self):
        """ """
        self.conn.close()       

class MyThread(threading.Thread):
    """ """

#    def __init__(self):
#        """ """
#        self.name = name
#        self.numThreads += 1

    def run(self):
        """ """
        print "%s started!" % self.getName()
        values = {'name' : 'Diego Antunes',
              'location' : 'Curitiba',
              'language' : 'Python' }

        req = urllib2.Request(CAPURL)
        
        try:
            #data = urllib.parse.urlencode(values)
            #req = urllib.request.Request(url, data)
            response = urllib2.urlopen(req)
        except URLError, e:
            if hasattr(e, 'reason'):
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'):
                print('The server couldn\'t fulfill the request.')
                print('Error code: ', e.code)
            else:
                print('no problems found')                

        imgData = response.read()
        imgFilename = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10)) + '.png'
        s = str(imgData)
        open(imgFilename, "w").write(s)
# This might be not necessary if the sleep on download works...        time.sleep(1.0)
        print "%s finished!" % self.getName()


def usage():
    """Returns usage message."""

    return "Usage: %s\n" \
        "-d\t--database\tUses a specific <database>\n" \
        "-o\t--download\n" \
        "-r\t--repetition\tDefines the number of repetitions\n" \
        "-h\t--help\t\tThis help" % sys.argv[0]

def download(rep):
    """ """
    home = os.path.abspath(os.environ['HOME'])
    dirName = join(home, 'tmp', 'img')
    if os.path.exists(dirName):
        os.chdir(dirName)
    else:
        sys.exit(1)

    # run the easy stuff, create a thread and make it download an captcha image
    i = 0
    for x in range(rep):
#        startTime = datetime.datetime.now()
        mythread = MyThread(name = "Thread-%d" % (x + 1))
        mythread.start()
        if i > 50:
            time.sleep(3)
            i = 0
        i += 1

def parseImgFile(dbHandler):
    """ """
    home = os.path.abspath(os.environ['HOME'])
    dirName = join(home, 'tmp', 'img')
    if os.path.exists(dirName):
        files = os.listdir(dirName)
        
        for filename in files:
            f = open(join(dirName, filename), 'rb')
            h = hashlib.sha1()
            h.update(f.read())
            fileHash = h.hexdigest()
            fileSize = getsize(join(dirName, filename))
            f.close()
            dbHandler.saveData(str(filename), str(fileHash), fileSize)
    else:
        print dirName + 'is not available'
        sys.exit(1)

    dbHandler.closeDB()

def main():
    database = None
    repetition = None
    down = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hod:r:", ["help", "download", "database=", "repetition="])
    except getopt.GetoptError as err:
        print(err)
        print usage()
        sys.exit(2)
    for option, value in opts:
        if option in ('-h', '--help'):
            print usage()
            sys.exit(0)
        elif option in ('-o', '--download'):
            down = True
        elif option in ('-r', '--repetition'):
            repetition = value
        elif option in ('-d', '--database'):
            database = value
        else:
            assert False, "unhandled option"

    # download the image files
    if repetition > 0 and down:
        download(int(repetition))

    # if a database was set, handle the downloaded files
    if database:
        myDB = IMBDataBase(database)
        parseImgFile(myDB)

if __name__ == '__main__':
    main()

