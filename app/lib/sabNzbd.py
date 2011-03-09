from app.config.cplog import CPLog
from app.lib import cleanHost
import base64
from urllib import urlencode
import urllib2
from tempfile import mkstemp
import re
import os


log = CPLog(__name__)

class sabNzbd():

    config = {}

    def __init__(self, config):
        self.config = config

    def conf(self, option):
        return self.config.get('Sabnzbd', option)

    def send(self, nzb, imdbId=None):
        log.info("Sending '%s' to SABnzbd." % nzb.name)

        if self.isDisabled():
            log.error("Config properties are not filled in correctly.")
            return False
        
        if self.conf('ppDir') and imdbId:
            try:
                ppScriptFn = self.buildPp(imdbId, self.getPpFile())
            except:
                log.info("Failed to create post-processing script.")
                ppScriptFn = False
            if not ppScriptFn:
                pp = False
            else:
                pp = True
        else:
            pp = False

        params = {
            'apikey': self.conf('apikey'),
            'cat': self.conf('category'),
            'mode': 'addurl',
            'name': nzb.url
        }

        # sabNzbd complains about "invalid archive file" for newzbin urls 
        # added using addurl, works fine with addid
        if nzb.addbyid:
            params['mode'] = 'addid'

        if self.conf('username'):
            params['ma_username'] = self.conf('username')
        if self.conf('password'):
            params['ma_password'] = self.conf('password')
        if pp:
            params['script'] = ppScriptFn

        url = cleanHost(self.conf('host')) + "sabnzbd/api?" + urlencode(params)

        log.info("URL: " + url)

        try:
            r = urllib2.urlopen(url, timeout = 30)
        except:
            try:
                # try https
                url = url.replace('http:', 'https:')
                r = urllib2.urlopen(url, timeout = 30)
            except:
                log.error("Unable to connect to SAB.")
                return False

        result = r.read().strip()
        if not result:
            log.error("SABnzbd didn't return anything.")
            return False

        log.debug("Result text from SAB: " + result)
        if result == "ok":
            log.info("NZB sent to SAB successfully.")
            return True
        elif result == "Missing authentication":
            log.error("Incorrect username/password.")
            return False
        else:
            log.error("Unknown error: " + result)
            return False

    def isDisabled(self):
        if self.conf('host') and self.conf('apikey'):
            return False
        else:
            return True
    
    def getPpFile(self):
        ppScriptHandle, ppScriptPath = mkstemp(suffix='.py', dir=self.conf('ppDir'))
        ppsh = os.fdopen(ppScriptHandle)

        ppsh.close()
        
        try:
            os.chmod(ppScriptPath, 0o777)
        except:
            log.info("Unable to set post-processing script permissions to 777 (may still work correctly): %s" % ppScriptPath)
        
        return ppScriptPath
        
    def buildPp(self, imdbId, ppScriptPath):
        scriptB64 = '''IyEvdXNyL2Jpbi9weXRob24KaW1wb3J0IG9zCmltcG9ydCBzeXMKcHJpbnQgIkNyZWF0aW5nIGNwLmNw
bmZvIGZvciAlcyIgJSBzeXMuYXJndlsxXQppbWRiSWQgPSB7W0lNREJJREhFUkVdfQpwYXRoID0gb3Mu
cGF0aC5qb2luKHN5cy5hcmd2WzFdLCAiY3AuY3BuZm8iKQp0cnk6CiBmID0gb3BlbihwYXRoLCAndycp
CmV4Y2VwdCBJT0Vycm9yOgogcHJpbnQgIlVuYWJsZSB0byBvcGVuICVzIGZvciB3cml0aW5nIiAlIHBh
dGgKIHN5cy5leGl0KDEpCnRyeToKIGYud3JpdGUob3MucGF0aC5iYXNlbmFtZShzeXMuYXJndlswXSkr
IlxuIitpbWRiSWQpCmV4Y2VwdDoKIHByaW50ICJVbmFibGUgdG8gd3JpdGUgdG8gZmlsZTogJXMiICUg
cGF0aAogc3lzLmV4aXQoMikKZi5jbG9zZSgpCnByaW50ICJXcm90ZSBpbWRiIGlkLCAlcywgdG8gZmls
ZTogJXMiICUgKGltZGJJZCwgcGF0aCkK'''
        
        script = re.sub(r"\{\[IMDBIDHERE\]\}", "'%s'" % imdbId, base64.b64decode(scriptB64))
        
        try:
            f = open(ppScriptPath, 'wb')
        except:
            log.info("Unable to open post-processing script for writing.  Check permissions: %s" % ppScriptPath)
            return False
        
        try:
            f.write(script)
            f.close()
        except:
            log.info("Unable to write to post-processing script. Check permissions: %s" % ppScriptPath)
            return False
        
        log.info("Wrote post-processing script to: %s" % ppScriptPath)
        
        return os.path.basename(ppScriptPath)