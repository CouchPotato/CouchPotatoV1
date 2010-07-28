from cherrypy.lib.auth import check_auth
from logging.config import _create_formatters, _install_handlers, \
    _install_loggers
import ConfigParser
import logging
import os.path
import webbrowser

log = logging.getLogger(__name__)

def clearAuthText(mypass):
    return mypass

def basicAuth(realm, users, encrypt = None):
    if check_auth(users, encrypt):
        return
    else:
        return

def launchBrowser(host, port):

    if host == '0.0.0.0':
        host = 'localhost'

    url = 'http://%s:%d' % (host, int(port))
    try:
        webbrowser.open(url, 2, 1)
    except:
        try:
            webbrowser.open(url, 1, 1)
        except:
            log.error('Could not launch a browser.')

def configLogging(fname, logPath):

    cp = ConfigParser.ConfigParser()
    if hasattr(cp, 'readfp') and hasattr(fname, 'readline'):
        cp.readfp(fname)
    else:
        cp.read(fname)

    cp.set('handler_accesslog', 'args', cp.get('handler_accesslog', 'args').replace('{logPath}', os.path.join(logPath, 'CouchPotato.log')))

    formatters = _create_formatters(cp)

    # critical section
    logging._acquireLock()
    try:
        logging._handlers.clear()
        del logging._handlerList[:]
        handlers = _install_handlers(cp, formatters)
        _install_loggers(cp, handlers, 1)
    finally:
        logging._releaseLock()

class flash():

    messages = {}

    def add(self, key, message):
        self.messages[key] = message

    def all(self):
        out = []
        for key in self.messages.keys():
            out.append(self.get(key))
        return out

    def get(self, key):
        message = self.messages.get(key)
        if message:
            self.remove(key)
            return message

    def remove(self, key):
        del self.messages[key]
