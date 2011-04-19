from app.config.cplog import CPLog
import base64
import cherrypy
import urllib
import urllib2
import tweepy

log = CPLog(__name__)

class TWITTER:

    def __init__(self):
        self.enabled = self.conf('enabled');
        self.access_key = self.conf('access_key')
        self.access_secret = self.conf('access_secret')
        self.consumer_key = '3POVsO3KW90LKZXyzPOjQ'
        self.consumer_secret = 'Qprb94hx9ucXvD4Wvg2Ctsk4PDK7CcQAKgCELXoyIjE'
        pass

    def conf(self, options):
        return cherrypy.config['config'].get('TWITTER', options)

    def notify(self, message):
        if not self.enabled:
            return
        
        message = '[CouchPotato] %s' % message
        message = message[:140] + (message[138:] and '..')
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_key, self.access_secret)
        api = tweepy.API(auth)
        try:
            api.update_status(message)
            log.info(u"Twitter notifications sent.")
        except tweepy.TweepError, e:
            log.error('Failed to post to twitter: ' +str(e))
        
        return

    def updateLibrary(self):
        #For uniformity reasons not removed
        return

    def authurl(self):
        
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth_url = auth.get_authorization_url()
        return auth_url
        
    def test(self):

        self.enabled = True
        self.notify('ZOMG Lazors Pewpewpew!')
