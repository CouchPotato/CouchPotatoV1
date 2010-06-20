from moviemanager.lib.provider.dataProvider import dataProvider
import logging
import os.path
import re
import time
import urllib
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

    def find(self, q, quality):
        log.info('Searching for movie: %s', q)

        arguments = urllib.urlencode({
            'action':'search',
            'q': self.searchString(q + ' ' + quality),
            'catid':self.getCatId(quality),
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
                xml = XMLTree.parse(data).findall('channel/item')

                results = []
                for nzb in xml:

                    id = int(self.gettextelement(nzb, "link").partition('nzbid=')[2])

                    size = self.gettextelement(nzb, "description").split('</a><br />')[1].split('">')[1]

                    new = self.feedItem()
                    new.id = id
                    new.name = self.gettextelement(nzb, "title")
                    new.date = str(self.gettextelement(nzb, "pubDate"))
                    new.size = size
                    results.append(new)

                log.info('Found: %s', results)
                return results
            except SyntaxError:
                log.error('Failed to parse XML response from NZBs.org')
                return False

    def getCatId(self, prefQuality):
        ''' Selecting category by quality '''

        for id, quality in self.catIds.iteritems():
            for q in quality:
                if q == prefQuality:
                    return id

    def getApiExt(self):
        return '&i=%s&h=%s' % (self.apiId, self.apiKey)
