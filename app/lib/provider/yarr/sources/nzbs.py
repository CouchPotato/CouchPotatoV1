from app.lib.provider.yarr.base import nzbBase
from urllib import urlencode
import logging
import time
import urllib2
import xml.etree.ElementTree as XMLTree

log = logging.getLogger(__name__)

class nzbs(nzbBase):
    """Api for nzbs"""

    downloadUrl = 'http://nzbs.org/index.php?action=getnzb&nzbid=%s%s'
    nfoUrl = 'http://nzbs.org/index.php?action=view&nzbid=%s&nfo=1'
    detailUrl = 'http://nzbs.org/index.php?action=view&nzbid=%s'

    config = None
    apiUrl = 'http://nzbs.org/rss.php'

    catIds = {
        4: ['720p', '1080p'],
        2: ['cam', 'ts', 'dvdrip', 'tc', 'brrip', 'r5', 'scr'],
        9: ['dvdr']
    }
    catBackupId = 't2'

    def __init__(self, config):
        log.info('Using NZBs.org provider')

        self.config = config

    def conf(self, option):
        return self.config.get('NZBsorg', option)

    def enabled(self):
        return self.conf('id') and self.conf('key') and str(self.config.get('NZB', 'enabled')).lower() == 'true'

    def find(self, movie, quality, type):

        results = []
        if not self.enabled():
            return results

        arguments = urlencode({
            'action':'search',
            'q': self.toSearchString(movie.name + ' ' + quality),
            'catid':self.getCatId(type),
            'i':self.conf('id'),
            'h':self.conf('key'),
            'age': self.config.get('NZB', 'retention')
        })
        url = "%s?%s" % (self.apiUrl, arguments)

        log.info('Search url: %s', url)

        data = urllib2.urlopen(url, timeout = self.timeout)

        if data:
            log.debug('Parsing NZBs.org RSS.')
            try:
                try:
                    xml = self.getItems(data)
                except:
                    log.error('No valid xml, to many requests? Try again in 15sec.')
                    time.sleep(15)
                    return self.find(movie, quality, type)

                for nzb in xml:

                    id = int(self.gettextelement(nzb, "link").partition('nzbid=')[2])

                    size = self.gettextelement(nzb, "description").split('</a><br />')[1].split('">')[1]

                    new = self.feedItem()
                    new.id = id
                    new.type = 'nzb'
                    new.name = self.gettextelement(nzb, "title")
                    new.date = time.mktime(time.strptime(str(self.gettextelement(nzb, "pubDate")), '%a, %d %b %Y %H:%M:%S +0000'))
                    new.size = size
                    new.url = self.downloadLink(id)
                    new.detailUrl = self.detailLink(id)
                    new.content = self.gettextelement(nzb, "description")
                    new.score = self.calcScore(new, movie)

                    if self.isCorrectMovie(new, movie):
                        results.append(new)
                        log.info('Found: %s', new.name)

                return results
            except SyntaxError:
                log.error('Failed to parse XML response from NZBs.org')
                return False

    def getItems(self, data):
        return XMLTree.parse(data).findall('channel/item')

    def getCatId(self, prefQuality):
        ''' Selecting category by quality '''

        for id, quality in self.catIds.iteritems():
            for q in quality:
                if q == prefQuality:
                    return id

        return self.catBackupId

    def getApiExt(self):
        return '&i=%s&h=%s' % (self.conf('id'), self.conf('key'))
