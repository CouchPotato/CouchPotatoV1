from cherrypy.lib.auth import check_auth
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
