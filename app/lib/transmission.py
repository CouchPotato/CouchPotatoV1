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
        
        # self.conf('username')
        try:
            tc = transmissionrpc.Client(self.conf('host'), port=self.conf('port'), user=self.conf('username'), password=self.conf('password'))
            tc.add_uri(torrent.url)
            return True

        except transmissionrpc.TransmissionError, e:
            log.error('Failed to send file to transmission: ' +str(e))
            return False

    def isDisabled(self):
        if self.conf('host'):
            return False
        else:
            return True