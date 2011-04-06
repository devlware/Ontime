#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
# Ontime
# Software to download the schedule for all public bus lines in Curitiba.
#
# Copyright (C) 2011 by Diego W. Antunes <devlware@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import urllib2
from urllib2 import Request, urlopen, URLError, HTTPError
from BeautifulSoup import BeautifulSoup
import os
from os.path import join, getsize
import tempfile
import random
import thread, time
import threading
import string
import sqlite3
import getopt, sys
import hashlib
import datetime

__version__ = "1.0"
__author__ = 'Diego W. Antunes'
__license__ = 'MIT'


class Config(object):
    """ """
    baseurl = 'http://www.urbs.curitiba.pr.gov.br'
    horariourl = 'PORTAL/tabelahorario/'
    captchaurl = 'PORTAL/tabelahorario/cap.php'
    silent = False
    
    DIAS = ["todos", "util", "sabado", "domingo"]
    #SENTIDOS = ["ida", "volta"]
    #PERIODOS = ["manha", "entrepico", "tarde"]
    
    DICT_DIAS = dict(zip("0123", DIAS))
    #DICT_SENTIDOS = dict(zip("IV", SENTIDOS))
    
    database = 'ontime.sqlite'
    CreateCaptchaCode = 'CREATE TABLE IF NOT EXISTS CaptchaCode \
        (pk INTEGER PRIMARY KEY NOT NULL, shasum TEXT, code TEXT)'
    CreateCaptchaSha1 = 'CREATE TABLE IF NOT EXISTS CaptchaSha1 \
        (pk INTEGER PRIMARY KEY NOT NULL, fn TEXT, shasum TEXT, size INTEGER, occurrences INTEGER)'
    CreateSchedule = 'CREATE TABLE IF NOT EXISTS Schedule \
        (pk INTEGER PRIMARY KEY NOT NULL, time TEXT, hasElevator INTEGER)'
    CreatePoint = 'CREATE TABLE IF NOT EXISTS Point \
        (pk INTEGER PRIMARY KEY NOT NULL, pointName TEXT validity TEXT, weekDay INTEGER)'
    CreateLine = 'CREATE TABLE IF NOT EXISTS Line \
        (pk INTEGER PRIMARY KEY NOT NULL, lineName TEXT)'

class OntimeException(Exception):
    """Captcha exception."""

class Schedule(object):
    """ """
    def __init__(self):
        pk
        time
        hasElevator = None

class Point(object):
    """ """
    def __init__(self):
        pk
        pointName
        validity
        weekDay
        scheduleID
        self.setWeekDay(weekDay)
    
    def setWeekDay(self, day):
        """ """
        self._weekDay = day

class Line(object):
    """ """

    def __init__(self, pk, lineName = None):
        self._pk
        self._lineName
        self.setLineName(lineName)

    def setPk(self, aCode)
        self._pk = aCode

    def setLineName(self, line):
        self._lineName = line

    def data(self):
        return self._data

class IMBDataBase(Config):
    """ """
    _conn = None
    _cursor = None

    def __init__(self):
        """ """
        self._conn = sqlite3.connect(Config.database)
        self._cursor = self._conn.cursor()

        try:
            # Create all the tables necessary to the project
            self._cursor.execute(CreateCaptchaSha1)
            self._cursor.execute(CreateCaptchaCode)
            self._cursor.execute(CreateSchedule)
            self._cursor.execute(CreatePoint)
            self._cursor.execute(CreateLine)
        except sqlite3.Error, e:
            print "Could not create table...", e.args[0]
            sys.exit(1)

        try:
            self._conn.commit()
        except sqlite3.Error, e:
            print "Could no commit table creation...", e.args[0]
        
    def saveData(self, fn, sha, size):
        """ """

        try:
            self._cursor.execute('SELECT pk, occurrences FROM CaptchaSha1 WHERE shasum = ?', (sha, ))
            row = self._cursor.fetchone()
            
            if row:
                pk = row[0]
                occ = row[1]
                try:
                    aTuple = (occ+1, pk, )
                    self._cursor.execute('UPDATE CaptchaSha1 SET occurrences = ? WHERE pk = ?', aTuple)
                    self._conn.commit()
                except sqlite3.Error, e:
                    print "An error occurred:", e.args[0]
                    sys.exit(1)
            else:
                t = (fn, sha, size, 1)
                try:
                    self._cursor.execute('INSERT INTO CaptchaSha1 (fn, shasum, size, occurrences) values (?, ?, ?, ?)', t)
                    self._conn.commit()
                except sqlite3.Error, e:
                    print "An error occurred:", e.args[0]
                    sys.exit(1)

        except sqlite3.Error, e:
            print "An error occurred:", e.args[0]
            sys.exit(2)

    def closeDB(self):
        """ """
        self._cursor.close()
        self._conn.close()

#class MyThread(threading.Thread):
class MyClass(ScheduleLine):
    """ """
    def __init__(self):
        """ """
        print "%s started!" % self.getName()
        ScheduleLine.__init__(self,  lineName, weekDay, captchaCode)

    def run(self):
        """ """
		cookie = urllib2.HTTPCookieProcessor()
		debug = urllib2.HTTPHandler()
		self._opener = urllib2.build_opener(debug, cookie)
		self._baseurl = baseurl
		self._data = { 'info' : [] }

		urllib2.install_opener(self._opener)

    def request(self, data = None):
    	"""Method used to request server/carrier data."""
		final = self._baseurl + '/' + url

		request = urllib2.Request(final)
		request.add_header('User-Agent', "Ontime/%s" % __version__)
		request.add_header('Accept-Encoding', 'gzip')
		if data is not None:
			request.add_data(data)
		descriptor = self._opener.open(request)
		data = descriptor.read()
		descriptor.close()

		soup = BeautifulSoup(data)
		handler(soup)


    def getCaptcha(self, data = None):

        req = urllib2.Request(captchaurl)
        
        try:
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
        imgFileString = str(imgData)
        h = hashlib.sha1()
        h.update(imgFileString)
        fileHash = h.hexdigest()

        self._cursor.execute('SELECT code FROM CaptchaCode WHERE shasum = ?', (fileHash, ))
        self.captchaCode = self._cursor.fetchone()[0]
        if not self.captchaCode:
            return None
        return self.captchaCode

    def _parseMenu(self, soup):
        box = soup.find('select')
        if box is None:
        else:
            boxd = box.findAll()

        menu = soup.find(id="cboLinha")
        menuOps = menu.findAll("option")
        a = []
        b = []
        for i in menuOps:
            a.append(i.contents[0])
            b.append(i.attrs[0][1])
            """
            Codigo para colocar no banco de dados as informacoes
            for i in range(len(a)):
                cursor.execute('INSERT INTO Line (lineName, pk) values (?, ?)', (a[i], int(str(b[i]))))
            """

        tipoDia = soup.find(id="cboTipoDia")
        opcoes = tipoDia.findAll("option") # retorna uma lista
        for i in opcoes:
            print i.contents
            print i.attrs[0][1]


        #como pegar o numero de um option
        a[1].attrs[0][1]
        # o retorno
        u'528'

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

