from app.lib.provider.yarr.base import torrentBase
from dateutil import relativedelta
from dateutil.parser import parse
from imdb.parser.http.bsouplxml._bsoup import SoupStrainer, BeautifulSoup
from urllib import quote_plus
import datetime
import logging
import os
import re
import time
import urllib2

log = logging.getLogger(__name__)

class tpb(torrentBase):
    """Api for the Pirate Bay"""

    downloadUrl = 'http://torrents.thepiratebay.org/%s/%s.torrent'
    nfoUrl = 'http://thepiratebay.org/torrent/%s'
    detailUrl = 'http://thepiratebay.org/torrent/%s'

    config = None
    apiUrl = 'http://thepiratebay.org/search/%s/0/7/%d'

    catIds = {
        207: ['720p', '1080p'],
        200: ['cam', 'ts', 'dvdrip', 'tc', 'r5', 'scr', 'brrip'],
        202: ['dvdr']
    }
    catBackupId = 200
    ignoreString = {
        '720p': ' -brrip -bdrip',
        '1080p': ' -brrip -bdrip'
    }

    def __init__(self, config):
        log.info('Using TPB.org provider')

        self.config = config

    def conf(self, option):
        return self.config.get('Torrents', option)

    def enabled(self):
        return self.conf('enabled') and self.conf('blackhole') and os.path.isdir(self.conf('blackhole'))

    def find(self, movie, quality, type):

        results = []
        if not self.enabled():
            return results

        url = self.apiUrl % (quote_plus(self.toSearchString(movie.name + ' ' + quality) + self.makeIgnoreString(type)), self.getCatId(type))

        log.info('Search url: %s', url)
        log.debug('Parsing TPB.org Search results.')

        try:
            data = urllib2.urlopen(url, timeout = self.timeout).read()
            pass
        except IOError:
            log.error('Failed to open %s.' % url)
            return results
        try:
            tables = SoupStrainer('table')
            html = BeautifulSoup(data, parseOnlyThese = tables)
            resultTable = html.find('table', attrs = {'id':'searchResult'})
            for result in resultTable.findAll('tr'):
                details = result.find('a', attrs = {'class':'detLink'})
                if details:
                    href = re.search('/(?P<id>\d+)/', details['href'])
                    id = href.group('id')
                    name = details.contents[0]
                    desc = result.find('font', attrs = {'class':'detDesc'}).contents[0].split(',')
                    date = ''
                    size = ''
                    for item in desc:
                        # Weird date stuff
                        if 'uploaded' in item.lower():
                            date = item.replace('Uploaded', '')
                            date = date.replace('Today', '')

                            # Do something with yesterday
                            yesterdayMinus = 0
                            if 'Y-day' in date:
                                date = date.replace('Y-day', '')
                                yesterdayMinus = 86400

                            datestring = date.replace('&nbsp;', ' ').strip()
                            date = int(time.mktime(parse(datestring).timetuple())) - yesterdayMinus
                        # size
                        elif 'size' in item.lower():
                            size = item.replace('Size', '')

                    seedleech = []
                    for td in result.findAll('td'):
                        try:
                            seedleech.append(int(td.contents[0]))
                        except ValueError:
                            pass

                    seeders = 0
                    leechers = 0
                    ratio = 0
                    if len(seedleech) == 2 and seedleech[0] > 0 and seedleech[1] > 0:
                        seeders = seedleech[0]
                        leechers = seedleech[1]
                        ratio = (leechers / seeders) * 5

                    # to item
                    new = self.feedItem()
                    new.id = id
                    new.type = 'torrent'
                    new.name = name
                    new.date = date
                    new.size = size
                    new.seeders = seeders
                    new.leechers = leechers
                    new.url = self.downloadLink(id, name)
                    new.detailUrl = self.detailLink(id)
                    new.content = self.getInfo(new.detailUrl)
                    new.score = self.calcScore(new, movie) + self.uploader(result) + ratio

                    if seeders > 0 and self.isCorrectMovie(new, movie) and (new.date + (int(self.conf('wait')) * 60 * 60) < time.time()):
                        results.append(new)
                        log.info('Found: %s', new.name)

            return results

        except AttributeError:
            log.info('No search results found.')

        return []
    
    def makeIgnoreString(self, type):
        ignore = self.ignoreString.get(type)
        return ignore if ignore else ''

    def uploader(self, html):
        score = 0
        if html.find('img', attr = {'alt':'VIP'}):
            score += 3
        if html.find('img', attr = {'alt':'Trusted'}):
            score += 1
        return score


    def getInfo(self, url):
        log.debug('Getting info: %s' % url)
        try:
            data = urllib2.urlopen(url, timeout = self.timeout).read()
            pass
        except IOError:
            log.error('Failed to open %s.' % url)
            return ''

        div = SoupStrainer('div')
        html = BeautifulSoup(data, parseOnlyThese = div)
        html = html.find('div', attrs = {'class':'nfo'})
        return str(html).decode("utf-8", "replace")

    def getCatId(self, prefQuality):
        ''' Selecting category by quality '''

        for id, quality in self.catIds.iteritems():
            for q in quality:
                if q == prefQuality:
                    return id

        return self.catBackupId

    def downloadLink(self, id, name):
        return self.downloadUrl % (id, quote_plus(name))
