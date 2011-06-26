from app.config.cplog import CPLog
import cherrypy
from pynma import pynma

log = CPLog(__name__)

class NMA:
    
    app_name = 'CouchPotato'
    
    def __init__(self):
        self.enabled = self.conf('enabled')
        self.apikey = self.conf('apikey')
    
    def conf(self, options):
        return cherrypy.config['config'].get('NMA', options)
    
    def notify(self,event, message):
        
        if not self.enabled:
            return
        
        p = pynma.PyNMA()
        p.addkey(self.apikey)
        response = p.push(self.app_name, event, message)
        
        # only check the first error, chances are they will all be the same
        if not response['a']['code'] == u'200':
            log.error('Could not send notification to NotifyMyAndroid. %s' % response['a']['message'])
            return False
        
        return response
        
    def test(self, apikey):
        
        self.enabled = True
        self.apikey = apikey
        
        self.notify('CouchPotato Test', 'ZOMG Lazors Pewpewpew')