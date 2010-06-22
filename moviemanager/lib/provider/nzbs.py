from moviemanager.lib.provider.dataProvider import dataProvider
import logging
import re
import time
import urllib
import datetime
import xml.etree.ElementTree as XMLTree

log = logging.getLogger(__name__)

class nzbs(dataProvider):
    """Api for nzbs"""

    downloadUrl = 'http://nzbs.org/index.php?action=getnzb&nzbid=%s%s'
    nfoUrl = 'http://nzbs.org/index.php?action=view&nzbid=%s&nfo=1'
    detailUrl = 'http://nzbs.org/index.php?action=view&nzbid=%s'

    apiUrl = 'http://nzbs.org/rss.php'
    apiId = 0
    apiKey = ''
    retention = 400

    catIds = {
        4: ['720p', '1080p'],
        2: ['cam', 'ts', 'dvdrip']
    }

    def __init__(self, config):
        log.info('Using NZBs.org provider')

        self.apiId = config.get('id')
        self.apiKey = config.get('key')
        self.retention = config.get('retention', 400)

    def find(self, movie):
        log.info('Searching for movie: %s', movie.name)

        arguments = urllib.urlencode({
            'action':'search',
            'q': self.searchString(movie.name + ' ' + movie.quality),
            'catid':self.getCatId(movie.quality),
            'i':self.apiId,
            'h':self.apiKey,
            'age':self.retention
        })
        url = "%s?%s" % (self.apiUrl, arguments)

        log.info('Search url: %s', url)

        data = urllib.urlopen(url)

        if data:
            log.info('Parsing NZBs.org RSS.')
            try:
                try:
                    xml = self.getItems(data)
                except e:
                    log.error('No valid xml, to many requests? Try again in 15sec.')
                    log.error(e)
                    time.sleep(15)
                    return self.find(movie)

                results = []
                for nzb in xml:

                    id = int(self.gettextelement(nzb, "link").partition('nzbid=')[2])

                    size = self.gettextelement(nzb, "description").split('</a><br />')[1].split('">')[1]

                    new = self.feedItem()
                    new.id = id
                    new.type = 'NZB.org'
                    new.name = self.gettextelement(nzb, "title")
                    new.date = datetime.datetime.strptime(str(self.gettextelement(nzb, "pubDate")), '%a, %d %b %Y %H:%M:%S +0000')
                    new.size = size
                    new.url = self.downloadLink(id)
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

    def getApiExt(self):
        return '&i=%s&h=%s' % (self.apiId, self.apiKey)
