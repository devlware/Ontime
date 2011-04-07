#!/usr/bin/python2.6 -O
# -*- coding: utf-8 -*-
# 
# OntimeNow
# This program was created to download all the bus lines from the database file
# defined on file ontime.sqlite.
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

import cookielib, urllib2, urllib
import sqlite3
import getopt, sys
import hashlib
import random
import string
import time
import os
from os.path import join
from urllib2 import Request, urlopen, URLError, HTTPError
from BeautifulSoup import BeautifulSoup

class OntimeNow:
    """ The program is pretty simple, just run it on the command line
        without any parameter and it should populate the html directory
        with 547 different file. Each file should have the bus schedule
        for a point in the line. """

    database = 'ontime.sqlite'
    debug = False

    baseurl = 'http://www.urbs.curitiba.pr.gov.br'
    indexurl = '/PORTAL/tabelahorario/index.php'
    lineurl = '/PORTAL/tabelahorario/tabela.php'
    captchaurl = '/PORTAL/tabelahorario/cap.php'
    user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; en-us) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27'
    contentType = 'application/x-www-form-urlencoded'
    accept = 'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5'

    def main(self):
        """ Main method, initialize some variables and call the main loop method. """

        _theCookie = None
        _cj = None
        _opener = None

        self.initUrlLib2Handlers()
        self.loopOverLines()

    def loopOverLines(self):
        """ This is where we loop over the available lines and call the
            downloader method. """

        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        cur.execute('SELECT pk FROM Line WHERE pk < 20')
        pkas = cur.fetchall()
        cur.close()
        conn.close()

        for i in pkas:
            self.downloadLineData(i[0])
            time.sleep(1)

    def updateLineTable(self, line):
        """ This method is used to save which"""

        print(type(line))
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        cur.execute('UPDATE Line SET downloaded = 1 WHERE pk=?', (line, ))
        conn.commit()
        cur.close()
        conn.close()
            
    def initUrlLib2Handlers(self):
        """ Initialize urllib2 handlers """

        self._theCookie = None
        self._cj = cookielib.CookieJar()
        cookie = urllib2.HTTPCookieProcessor(self._cj)
        debug = urllib2.HTTPHandler()
        self._opener = urllib2.build_opener(debug, cookie)
        urllib2.install_opener(self._opener)
    
    def createHeader(self, url, withCookie = False, withReferer = None):
        """ Create a default header for the requests """

        request = urllib2.Request(url)
        request.add_header('User-Agent', self.user_agent)
        request.add_header('Content-Type', self.contentType)
        request.add_header('Accept', self.accept)
        request.add_header('Accept-Encoding', 'gzip, deflate')
        request.add_header('Accept-Language', 'en-us')
        request.add_header('Referer', withReferer)

        if withCookie:
            cookieStr = self._theCookie.name + '=' + self._theCookie.value
            self._log(cookieStr)
            request.add_header('Cookie', cookieStr)
        else:
            request.add_header('Cookie', '')
            
        return request

    def downloadLineData(self, line = 1):
        """ Here we have some fun! """

        # Create a request to get the index page
        aUrl = self.baseurl + self.indexurl
        referer = 'http://www.urbs.curitiba.pr.gov.br'
        descriptor = self.runRequest(self.createHeader(aUrl, False, referer))

        cookies = []
        for i in self._cj:
            cookies.append(i)
        if cookies[0]:
            self._theCookie = cookies[0]
        descriptor.close()

        # Now, create a request to get the image captcha
        referer = 'http://www.urbs.curitiba.pr.gov.br/PORTAL/tabelahorario/'
        request = self.createHeader(self.baseurl + self.captchaurl, True, referer)
        descriptor =  self.runRequest(request)

        # Read the response which should be an image.
        imgFileString = str(descriptor.read())
        descriptor.close()
        h = hashlib.sha1()
        h.update(imgFileString)
        fileHash = h.hexdigest()
        self._log(fileHash)

        if self.debug:
            imgFilename = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8)) + '.png'
            fd = open(imgFilename, 'w+')
            fd.write(imgFileString)
            fd.close()

        # Query the database for the captcha code based on the hash
        captcha = self.queryDB(fileHash)

        # Create the POST message
        values = ('cboLinha'     , line), \
                  ('cboTipoDia'  , '0'), \
                  ('cpt'         , captcha), \
                  ('btnAcesso'   , 'Consultar')

        referer = 'http://www.urbs.curitiba.pr.gov.br/PORTAL/tabelahorario/'
        request = self.createHeader(self.baseurl + self.lineurl, True, referer)
        request.add_data(urllib.urlencode(values))
        descriptor = self.runRequest(request)

        # Change dir so we save the line data for future parse
        home = os.path.abspath(os.environ['PWD'])
        dirName = join(home, 'html')
        if os.path.exists(dirName):
            os.chdir(dirName)
        else:
            self._log('Html directory does not exist, exiting...')
            sys.exit(1)

        htmlData = descriptor.read()
        descriptor.close()

        # Now, save it please!
        htmlFilename = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16)) + '.html'
        fd = open(htmlFilename, 'w')
        fd.write(htmlData)
        fd.close()

        os.chdir(home)

        # Some tests on how parse data... still not working and should be moved to another py file
        soup = BeautifulSoup(htmlData)
        box = soup.findAll('font' ,{'class' : 'textoPonto'})
#        box = soup.findAll("font", {"class" : "textoLinha"})
        if box:
            for i in box:
                print(i.contents)
                self.updateLineTable(line)

    def runRequest(self, urlRequest):
        try:
            descriptor = self._opener.open(urlRequest)
        except URLError, e:
            if hasattr(e, 'reason'):
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'):
                print('The server couldn\'t fulfill the request.')
                print('Error code: ', e.code)
            sys.exit(1)

        return descriptor

    def queryDB(self, value):
        """ Open database and check if the hash for the captcha image is
            available. """

        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        cur.execute('SELECT code FROM CaptchaCode WHERE shasum = ?', (value, ))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            self._log('Captcha code not available')
            sys.exit(1)
        return row[0]

    def _log(self, string):
        """ Logs strings """

        if self.debug:
            print(string)

if __name__ == '__main__':
    OntimeNow().main()
