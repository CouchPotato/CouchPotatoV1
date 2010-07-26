from app.lib.provider.yarr.base import nzbBase
from dateutil.parser import parse
from urllib import urlencode
from urllib2 import URLError
import logging
import time
import urllib2

log = logging.getLogger(__name__)

class nzbMatrix(nzbBase):
    """Api for NZBMatrix"""

    name = 'NZBMatrix'
    downloadUrl = 'http://nzbmatrix.com/api-nzb-download.php?id=%s%s'
    detailUrl = 'http://nzbmatrix.com/api-nzb-details.php?id=%s%s'
    searchUrl = 'http://rss.nzbmatrix.com/rss.php'

    catIds = {
        42: ['720p', '1080p'],
        2: ['cam', 'ts', 'dvdrip', 'tc', 'r5', 'scr'],
        54: ['brrip'],
        1: ['dvdr']
    }
    catBackupId = 2

    def __init__(self, config):
        log.info('Using NZBMatrix provider')

        self.config = config

    def conf(self, option):
        return self.config.get('NZBMatrix', option)

    def enabled(self):
        return self.config.get('NZB', 'enabled') and self.conf('username') and self.conf('apikey')

    def find(self, movie, quality, type, retry = False):

        results = []
        if not self.enabled() or not self.isAvailable(self.searchUrl):
            return results

        arguments = urlencode({
            'term': self.toSearchString(movie.name + ' ' + quality),
            'subcat':self.getCatId(type),
            'username':self.conf('username'),
            'apikey':self.conf('apikey')
        })
        url = "%s?%s" % (self.searchUrl, arguments)

        log.info('Searching: %s', url)

        try:
            data = urllib2.urlopen(url, timeout = self.timeout)
        except (IOError, URLError):
            log.error('Failed to open %s.' % url)
            return results

        if data:
            try:
                try:
                    xml = self.getItems(data)
                except:
                    if retry == False:
                        log.error('No valid xml, to many requests? Try again in 15sec.')
                        time.sleep(15)
                        return self.find(movie, quality, type, retry = True)
                    else:
                        log.error('Failed again.. disable %s for 15min.' % self.name)
                        self.available = False
                        return results

                results = []
                for nzb in xml:

                    id = int(self.gettextelement(nzb, "link").split('&')[0].partition('id=')[2])
                    size = self.gettextelement(nzb, "description").split('<br /><b>')[2].split('> ')[1]
                    date = str(self.gettextelement(nzb, "description").split('<br /><b>')[3].partition('Added:</b> ')[2])

                    new = self.feedItem()
                    new.id = id
                    new.type = 'nzb'
                    new.name = self.gettextelement(nzb, "title")
                    new.date = int(time.mktime(parse(date).timetuple()))
                    new.size = self.parseSize(size)
                    new.url = self.downloadLink(id)
                    new.content = self.gettextelement(nzb, "description")
                    new.score = self.calcScore(new, movie)

                    if new.date > time.time() - (int(self.config.get('NZB', 'retention')) * 24 * 60 * 60) and self.isCorrectMovie(new, movie, type):
                        results.append(new)
                        log.info('Found: %s', new.name)

                return results
            except SyntaxError:
                log.error('Failed to parse XML response from NZBMatrix.com')
                return False

    def getApiExt(self):
        return '&username=%s&apikey=%s' % (self.conf('username'), self.conf('apikey'))
