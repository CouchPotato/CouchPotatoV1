from cherrypy.lib.auth import check_auth
from logging.config import _create_formatters, _install_handlers, _install_loggers
import ConfigParser
import logging
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

def configLogging(fname, basePath):

    cp = ConfigParser.ConfigParser()
    if hasattr(cp, 'readfp') and hasattr(fname, 'readline'):
        cp.readfp(fname)
    else:
        cp.read(fname)

    cp.set('handler_accesslog', 'args', cp.get('handler_accesslog', 'args').replace('{basePath}', basePath))

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
