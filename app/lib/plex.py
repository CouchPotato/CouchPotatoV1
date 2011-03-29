from app.config.cplog import CPLog
import base64
import cherrypy
import urllib
import urllib2
from xml.dom import minidom

log = CPLog(__name__)

class PLEX:

    hosts = []

    def __init__(self):
        self.enabled = self.conf('enabled');
        self.hosts = [x.strip() for x in self.conf('host').split(",")]
        pass

    def conf(self, options):
        return cherrypy.config['config'].get('PLEX', options)

    def notify(self, message):
        #For uniformity reasons not removed
        return

    def updateLibrary(self):
        if not self.enabled:
            return
            
        hosts = self.hosts

        for host in hosts:
            request = self.libraryUpdater(host)

            if not request:
                return False

        log.info('Plex library update initiated')
        return True

    def libraryUpdater(self, host):

        source_type = ['movie'] # Valid values: artist (for music), movie, show (for tv)
        base_url = 'http://%s/library/sections' % host
        refresh_url = '%s/%%s/refresh' % base_url

        try:
          xml_sections = minidom.parse(urllib.urlopen(base_url))
          sections = xml_sections.getElementsByTagName('Directory')
          for s in sections:
            if s.getAttribute('type') in source_type:
              url = refresh_url % s.getAttribute('key')
              x = urllib.urlopen(url)
        except:
          log.error('Plex library update failed')
          return False

        return True

    def test(self, hosts):

        self.enabled = True
        self.hosts = [x.strip() for x in hosts.split(",")]

        self.updateLibrary()
