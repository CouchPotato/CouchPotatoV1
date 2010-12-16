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

    def send(self, nzb, imdbId):
        log.info("Sending '%s' to SABnzbd." % nzb.name)

        if self.isDisabled():
            log.error("Config properties are not filled in correctly.")
            return False
        
        if self.conf('ppDir'):
            ppScriptFn = self.buildPp(imdbId, self.getPpFile())
            pp = True
            #
            #try:
            #    
            #except:
            #    pp = False
            #    log.info("Unable to create post-processing script for sabnzbd")
            #    import pdb; pdb.set_trace()
            #    pass
        else:
            pp = False

        params = {
            'apikey': self.conf('apikey'),
            'cat': self.conf('category'),
            'mode': 'addurl',
            'name': nzb.url
        }

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
        try:
            ppsh.close()
        except:
            import pdb; pdb.set_trace()
        
        os.chmod(ppScriptPath, 0o777)
        #try:
        #    
        #except:
        #    log.info("Unable to set post-processing script to 777: %s" % ppScriptPath)
        
        return ppScriptPath
        
    def buildPp(self, imdbId, ppScriptPath):
        scriptB64 = '''IyEvdXNyL2Jpbi9weXRob24KaW1wb3J0IG9zCmltcG9ydCBzeXMKCnByaW50ICJDcmVhdGluZyBDUC5u
Zm8gZm9yICVzIiAlIHN5cy5hcmd2WzFdCgppbWRiSWQgPSB7W0lNREJJREhFUkVdfQoKcGF0aCA9IG9z
LnBhdGguam9pbihzeXMuYXJndlsxXSwgIkNQLm5mbyIpCnRyeToKICAgIGYgPSBvcGVuKHBhdGgsICd3
JykKZXhjZXB0IElPRXJyb3I6CiAgICBwcmludCAiVW5hYmxlIHRvIG9wZW4gJXMgZm9yIHdyaXRpbmci
ICUgcGF0aAogICAgc3lzLmV4aXQoMSkKCnRyeToKICAgIGYud3JpdGUoJ3R0MDkxNDc5OCcpCmV4Y2Vw
dDoKICAgIHByaW50ICJVbmFibGUgdG8gd3JpdGUgdG8gZmlsZTogJXMiICUgcGF0aAogICAgc3lzLmV4
aXQoMikKICAgIApmLmNsb3NlKCkKcHJpbnQgIldyb3RlIGltZGIgaWQsICVzLCB0byBmaWxlOiAlcyIg
JSAoaW1kYklkLCBwYXRoKQo='''
        
        script = re.sub(r"\{\[IMDBIDHERE\]\}", "'%s'" % imdbId, base64.b64decode(scriptB64))
        
        f = open(ppScriptPath, 'wb')
        f.write(script)
        f.close()
        
        
        #try:
        #    fileHandle.write(script)
        #    f.close()
        #except:
        #    log.info("Unable to write to post-processing script, check permisisons: %s" % ppScriptPath)
        #    return False
        
        
        
        return os.path.basename(ppScriptPath)