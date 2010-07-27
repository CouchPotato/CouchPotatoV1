import logging
from urllib import urlencode
import urllib2

log = logging.getLogger(__name__)

class sabNzbd():

    config = {}

    def __init__(self, config):
        self.config = config

    def conf(self, option):
        return self.config.get('Sabnzbd', option)

    def send(self, nzb):
        log.info("Sending '%s' to SABnzbd." % nzb.name)

        if self.isDisabled():
            log.error("Config properties are not filled in correctly.")
            return False

        url = 'http://' + self.conf('host') + "/sabnzbd/api?" + urlencode({
            'ma_username': self.conf('username'),
            'ma_password': self.conf('password'),
            'apikey': self.conf('apikey'),
            'cat': self.conf('category'),
            'mode': 'addurl',
            'name': nzb.url
        })

        log.info("URL: " + url)

        try:
            r = urllib2.urlopen(url, timeout = 10)
        except:
            try:
                # try https
                url = url.replace('http:', 'https:')
                r = urllib2.urlopen(url, timeout = 10)
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
