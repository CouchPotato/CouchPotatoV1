from app.config.cplog import CPLog
from app.lib import cleanHost
import transmissionrpc
import re
import os

log = CPLog(__name__)

class transmission():

    config = {}

    def __init__(self, config):
        self.config = config

    def conf(self, option):
        return self.config.get('Transmission', option)

    def send(self, torrent, imdbId=None):
        log.info("Sending '%s' to Transmission." % torrent.name)

        if self.isDisabled():
            log.error("Config properties are not filled in correctly.")
            return False
        
        # Load host from config and split out port.
        host = self.conf('host').split(':')
        if not host[1].isdigit():
            log.error("Config properties are not filled in correctly, port is missing.")
            return False
        
        # Set parameters for Transmission
        params = {}
        
        if not (self.conf('paused') == ''):
            params['paused'] = self.conf('paused')

        if self.config.get('Renamer', 'enabled'):
            params['download_dir'] = self.config.get('Renamer', 'download')
        
        try:
            tc = transmissionrpc.Client(host[0], port = host[1], user = self.conf('username'), password = self.conf('password'))
            tc.add_uri(torrent.url, **params)
            return True

        except transmissionrpc.TransmissionError, e:
            log.error('Failed to send link to transmission: ' +str(e))
            return False

    def isDisabled(self):
        if self.conf('host'):
            return False
        else:
            return True