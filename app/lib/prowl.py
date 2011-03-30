from app.config.cplog import CPLog
import base64
import cherrypy
import urllib
import urllib2
from httplib import HTTPSConnection
from urllib import urlencode

log = CPLog(__name__)

class PROWL:

    keys = []
    priority = []

    def __init__(self):
        self.enabled = self.conf('enabled');
        self.keys = self.conf('keys')
        self.priority = self.conf('priority')
        pass

    def conf(self, options):
        return cherrypy.config['config'].get('PROWL', options)

    def notify(self, message, event):
        if not self.enabled:
            return

        http_handler = HTTPSConnection("api.prowlapp.com")
                                                
        data = {'apikey': self.keys,
                'application': 'CouchPotato',
                'event': event,
                'description': message,
                'priority': self.priority }

        http_handler.request("POST",
                                "/publicapi/add",
                                headers = {'Content-type': "application/x-www-form-urlencoded"},
                                body = urlencode(data))
        response = http_handler.getresponse()
        request_status = response.status

        if request_status == 200:
                log.info(u"Prowl notifications sent.")
                return True
        elif request_status == 401: 
                log.error(u"Prowl auth failed: %s" % response.reason)
                return False
        else:
                log.error(u"Prowl notification failed.")
                return False

    def updateLibrary(self):
        #For uniformity reasons not removed
        return

    def test(self, keys, priority):

        self.enabled = True
        self.keys = keys
        self.priority = priority

        self.notify('ZOMG Lazors Pewpewpew!', 'Test Message')
