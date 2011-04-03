#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
# Test
# This app is used to test the execution of Ontime.
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
import urllib
import sqlite3
import getopt, sys
import hashlib
from urllib2 import Request, urlopen, URLError, HTTPError
from BeautifulSoup import BeautifulSoup

baseurl = 'http://www.urbs.curitiba.pr.gov.br'
url = '/PORTAL/tabelahorario/tabela.php/cboLinha=342&cboTipoDia=0&cpt=%s&btnAcesso=Consultar'
captchaurl = 'http://www.urbs.curitiba.pr.gov.br/PORTAL/tabelahorario/cap.php'
user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; en-us) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27'

cookie = urllib2.HTTPCookieProcessor()
debug = urllib2.HTTPHandler()
opener = urllib2.build_opener(debug, cookie)
urllib2.install_opener(opener)

# Create a request to download the captcha image
request = urllib2.Request(captchaurl)
request.add_header('User-Agent', user_agent)
request.add_header('Content-Type', 'application/x-www-form-urlencoded')
request.add_header('Accept', 'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5')
request.add_header('Accept-Encoding', 'gzip, deflate')
request.add_header('Accept-Language', 'en-us')
response = urllib2.urlopen(request)

# Read the response which should be an image and calculates the hash.
imgData = response.read()
imgFileString = str(imgData)
h = hashlib.sha1()
h.update(imgFileString)
fileHash = h.hexdigest()
print fileHash

# Open database and check if the hash for the captcha image is on db.
conn = sqlite3.connect('mydb.db')
cur = conn.cursor()
cur.execute('SELECT code FROM CaptchaCode WHERE shasum = ?', (fileHash, ))
captchaCode = cur.fetchone()[0]
cur.close()
conn.close()

if captchaCode is None:
    print('Captcha code not available')
    sys.exit(1)


url = '/PORTAL/tabelahorario/tabela.php'
final = baseurl + url
values = ('cboLinha'    , '342'), \
          ('cboTipoDia'  , '0'), \
          ('cpt'         , captchaCode), \
          ('btnAcesso'   , 'Consultar')
data = urllib.urlencode(values)

# Create another request to get the data from the server. Notice that 
# the bus line and line day are hardcode above because this is just a test.
req = urllib2.Request(url, data)

print(final)
request = urllib2.Request(final, data)

request.add_header('User-Agent', user_agent)
request.add_header('Content-Type', 'application/x-www-form-urlencoded')
request.add_header('Accept', 'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5')
request.add_header('Accept-Encoding', 'gzip, deflate')
request.add_header('Accept-Language', 'en-us')

try:
    descriptor = opener.open(request)
    data = descriptor.read()
    descriptor.close()
except URLError, e:
    if hasattr(e, 'reason'):
        print('We failed to reach a server.')
        print('Reason: ', e.reason)
    elif hasattr(e, 'code'):
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
    else:
        print('no problems found')                

# here we should be able to parse all the data from the server.
soup = BeautifulSoup(data)
print(soup)

