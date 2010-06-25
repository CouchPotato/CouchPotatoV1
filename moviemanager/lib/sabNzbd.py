import logging
import urllib

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

        url = 'http://' + self.conf('host') + "/sabnzbd/api?" + urllib.urlencode({
            'ma_username': self.conf('username'),
            'ma_password': self.conf('password'),
            'apikey': self.conf('apikey'),
            'cat': self.conf('category'),
            'mode': 'addurl',
            'name': nzb.url
        })

        log.info("URL: " + url)

        try:
            r = urllib.urlopen(url)
        except:
            log.error("Unable to connect to SAB.")
            return False

        if r == None:
            log.error("SABnzbd didn't return anything.")
            return False

        result = r.readlines()
        if len(result) == 0:
            log.error("SABnzbd didn't return anything.")
            return False

        sabText = result[0].strip()

        log.info("Result text from SAB: " + sabText)

        if sabText == "ok":
            log.info("NZB sent to SAB successfully.")
            return True
        elif sabText == "Missing authentication":
            log.error("Incorrect username/password.")
            return False
        else:
            log.error("Unknown error: " + sabText)
            return False
        
        return True

    def isDisabled(self):
        if self.conf('host') and self.conf('apikey'):
            return False
        else:
            return True
