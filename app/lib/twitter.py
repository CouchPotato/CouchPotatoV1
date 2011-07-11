from app.config.cplog import CPLog

import cherrypy
import urllib
import oauth2 as oauth
import pythontwitter as twitter

try:
    from urlparse import parse_qsl #@UnusedImport
except:
    from cgi import parse_qsl #@Reimport

log = CPLog(__name__)

class Twitter:

    consumer_key = "OzYPCnKBIW7sLh3MOYCw"
    consumer_secret = "VATWCcvy0kK0wGyyu9phFeMgTn4t1O4yaklEzaXfDqM"

    REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
    ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
    AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
    SIGNIN_URL = 'https://api.twitter.com/oauth/authenticate'

    def __init__(self):
        self.enabled = self.get_conf('enabled')
        self.username = self.get_conf('username')
        self.password = self.get_conf('password')
        self.isAuthenticated = self.get_conf('isAuthenticated')

    def get_conf(self, options):
            return cherrypy.config['config'].get('Twitter', options)

    def set_conf(self, options, value):
        cherrypy.config['config'].set('Twitter', options, value)

    def save_conf(self):
        cherrypy.config['config'].save()

    def notify(self, event, message):
        if not self.enabled or not self.isAuthenticated:
            return

        username = self.consumer_key
        password = self.consumer_secret
        access_token_key = self.get_conf('username')
        access_token_secret = self.get_conf('password')

        log.info('Sending tweet: '+message)

        api = twitter.Api(username, password, access_token_key, access_token_secret)

        try:
            api.PostUpdate(message)
        except Exception, e:
            log.error('Error sending tweet: '+str(e))
            return False

        return True

    def test(self):
        self.enabled = True
        self.notify('CouchPotato Test', 'ZOMG Lazors Pewpewpew!')

    def get_authorization(self):

        oauth_consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        oauth_client = oauth.Client(oauth_consumer)

        log.info('Requesting access token from Twitter')

        callbackURL = 'http://127.0.0.1:5000/config/twitterAuth/'
        
        resp, content = oauth_client.request(self.REQUEST_TOKEN_URL, 'POST', body=urllib.urlencode({'oauth_callback':callbackURL}))

        if resp['status'] != '200':
            log.error('Invalid response from Twitter requesting temp token: %s' % resp['status'])
        else:
            request_token = dict(parse_qsl(content))

            self.set_conf('username', request_token['oauth_token'])
            self.set_conf('password', request_token['oauth_token_secret'])
            self.save_conf()

            return self.AUTHORIZATION_URL+"?oauth_token="+ request_token['oauth_token']

    def get_credentials(self, key):
            request_token = {}

            request_token['oauth_token'] = self.get_conf('username')
            request_token['oauth_token_secret'] = self.get_conf('password')
            request_token['oauth_callback_confirmed'] = 'true'

            token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
            token.set_verifier(key)

            log.info('Generating and signing request for an access token using key '+key)

            oauth_consumer = oauth.Consumer(key=self.consumer_key, secret=self.consumer_secret)
            log.info('oauth_consumer: '+str(oauth_consumer))
            oauth_client = oauth.Client(oauth_consumer, token)
            log.info('oauth_client: '+str(oauth_client))
            resp, content = oauth_client.request(self.ACCESS_TOKEN_URL, method='POST', body='oauth_verifier=%s' % key)
            log.info('resp, content: '+str(resp)+','+str(content))

            access_token = dict(parse_qsl(content))
            log.info('access_token: '+str(access_token))

            log.info('resp[status] = '+str(resp['status']))
            if resp['status'] != '200':
                log.error('The request for a token did not succeed: '+str(resp['status']))
                return False
            else:
                log.info('Your Twitter access token is %s' % access_token['oauth_token'])
                log.info('Access token secret is %s' % access_token['oauth_token_secret'])
                self.set_conf('username', access_token['oauth_token'])
                self.set_conf('password', access_token['oauth_token_secret'])
                self.set_conf('isAuthenticated', True)
                self.save_conf()
                return True
