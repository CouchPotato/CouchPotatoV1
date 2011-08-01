from app import latinToAscii
from app.config.cplog import CPLog
from string import ascii_letters, digits
from urllib2 import URLError
import cherrypy
import math
import os
import platform
import re
import time
import unicodedata
import urllib2
import xml.etree.ElementTree as XMLTree

log = CPLog(__name__)

class rss:

    timeout = 10

    lastUse = 0
    timeBetween = 1

    available = True
    availableCheck = 0

    userAgents = {
        'linux': 'Mozilla/5.0 (X11; Linux x86_64; rv:5.0) Gecko/20100101 Firefox/5.0 Firefox/5.0',
        'windows': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:5.0) Gecko/20110619 Firefox/5.0',
        'osx': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:5.0) Gecko/20100101 Firefox/5.0'
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Accept-Encoding': '',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0'
    }

    def toSaveString(self, string):
        string = latinToAscii(string)
        string = ''.join((c for c in unicodedata.normalize('NFD', unicode(string)) if unicodedata.category(c) != 'Mn'))
        safe_chars = ascii_letters + digits + '_ -.,\':!?'
        r = ''.join([char if char in safe_chars else ' ' for char in string])
        return re.sub('\s+' , ' ', r)

    def toSearchString(self, string):
        string = latinToAscii(string)
        string = ''.join((c for c in unicodedata.normalize('NFD', unicode(string)) if unicodedata.category(c) != 'Mn'))
        safe_chars = ascii_letters + digits + ' \''
        r = ''.join([char if char in safe_chars else ' ' for char in string])
        return re.sub('\s+' , ' ', r).replace('\'s', 's').replace('\'', ' ')

    def simplifyString(self, original):
        split = re.split('\W+', original.lower())
        return ' '.join(split)

    def gettextelements(self, xml, path):
        ''' Find elements and return tree'''

        textelements = []
        try:
            elements = xml.findall(path)
        except:
            return
        for element in elements:
            textelements.append(element.text)
        return textelements

    def gettextelement(self, xml, path):
        ''' Find element and return text'''

        try:
            return xml.find(path).text
        except:
            return

    def getItems(self, data, path = 'channel/item'):
        try:
            return XMLTree.parse(data).findall(path)
        except Exception, e:
            log.error('Error parsing RSS. %s' % e)
            return []

    def wait(self):
        now = time.time()
        wait = math.ceil(self.lastUse - now + self.timeBetween)
        if wait > 0:
            log.debug('Waiting for %s, %d seconds' % (self.name, wait))
            time.sleep(wait)

    def isAvailable(self, testUrl):

        if cherrypy.config.get('debug'): return True

        now = time.time()

        if self.availableCheck < now - 900:
            self.availableCheck = now
            try:
                self.urlopen(testUrl, 30)
                self.available = True
            except (IOError, URLError):
                log.error('%s unavailable, trying again in an 15 minutes.' % self.name)
                self.available = False

        return self.available


    def urlopen(self, url, timeout = 10, username = '', password = ''):

        self.wait()

        try:
            if username is not '' and password is not '':
                passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
                passman.add_password(None, url, username, password)
                authhandler = urllib2.HTTPBasicAuthHandler(passman)
                opener = urllib2.build_opener(authhandler)
                log.debug('Opening "%s" with password' % url)
                data = opener.open(url, timeout = timeout)
            else:
                log.debug('Opening "%s"' % url)

                req = urllib2.Request(url)

                # User Agent based on OS
                if 'videoeta.com' in url.lower():
                    if os.name == 'nt':
                        userAgent = self.userAgents['windows']
                    elif 'Darwin' in platform.platform():
                        userAgent = self.userAgents['osx']
                    else:
                        userAgent = self.userAgents['linux']

                    req.add_header('User-Agent', userAgent)

                    for type, value in self.headers.iteritems():
                        req.add_header(type, value)

                data = urllib2.urlopen(req, timeout = self.timeout)

        except IOError, e:
            log.error('Something went wrong in urlopen: %s' % e)
            data = ''

        self.lastUse = time.time()

        return data

    def correctName(self, checkName, movieName):

        checkWords = re.split('\W+', self.toSearchString(checkName).lower())
        movieWords = re.split('\W+', self.toSearchString(movieName).lower())

        found = 0
        for word in movieWords:
            if word in checkWords:
                found += 1

        return found == len(movieWords)

    class feedItem(dict):
        ''' NZB item '''

        def __getattr__(self, attr):
            return self.get(attr, None)

        __setattr__ = dict.__setitem__
        __delattr__ = dict.__delitem__
