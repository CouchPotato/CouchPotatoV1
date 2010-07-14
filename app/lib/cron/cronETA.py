from app.lib.cron.cronBase import cronBase
from app.lib.provider.rss import rss
from imdb.parser.http.bsouplxml._bsoup import BeautifulSoup, SoupStrainer
import Queue
import logging
import re
import time
import urllib

etaQueue = Queue.Queue()
log = logging.getLogger(__name__)

class etaCron(rss, cronBase):

    searchUrl = 'http://videoeta.com/search/'
    detailUrl = 'http://videoeta.com/movie/'

    def run(self):
        log.info('MovieETA thread is running.')

        timeout = 0.1 if self.debug else 1
        while True and not self.abort:
            try:
                movie = etaQueue.get(timeout = timeout)

                #do a search
                self.running = True
                result = self.search(movie)
                if result:
                    self.save(movie, result)

                etaQueue.task_done()
                time.sleep(timeout)
                self.running = False
            except Queue.Empty:
                pass


        log.info('MovieETA thread shutting down.')

    def save(self, movie, result):
        
        from app.config.db import MovieETA, Session as Db
        row = Db.query(MovieETA).filter_by(movieId = movie.id).first()
        if not row:
            row = MovieETA()
            Db.add(row)
            Db.flush()

        row.movieId = movie.id
        row.videoEtaId = result['id']
        row.theater = result['theater']
        row.dvd = result['dvd']
        row.bluray = result['bluray']
        Db.flush()

    def search(self, movie):

        # Already found it, just update the stuff
        if movie.eta and movie.eta.videoEtaId:
            log.info('Updating VideoETA for %s.' % movie.name)
            return self.getDetails(movie.eta.videoEtaId)

        # Do search
        log.info('Searching VideoETA for %s.' % movie.name)
        arguments = urllib.urlencode({
            'search_query':self.toSearchString(movie.name)
        })
        url = "%s?%s" % (self.searchUrl, arguments)

        log.info('Search url: %s.', url)

        results = self.getItems(urllib.urlopen(url).read())

        if results:
            for result in results:
                if str(movie.year).lower() != 'none' and self.toSearchString(result.get('name')).lower() == self.toSearchString(movie.name).lower() and result.get('year') == int(movie.year):
                    log.debug('MovieETA perfect match!')
                    return self.getDetails(result.get('id'))

    def getDetails(self, id):
        url = self.detailUrl + str(id)

        log.info('Scanning %s.', url)

        try:
            data = urllib.urlopen(url).read()
            pass
        except IOError:
            log.error('Failed to open %s.' % url)
            return False

        # Search for theater release
        theaterDate = 0
        try:
            theaterLink = SoupStrainer('a', href = re.compile('/month_theaters.html\?'))
            theater = BeautifulSoup(data, parseOnlyThese = theaterLink)
            theaterDate = self.parseDate(theater.a.contents[0])
        except AttributeError:
            log.info('No Theater release info found.')

        # Search for dvd release date
        dvdDate = 0
        try:
            dvdLink = SoupStrainer('a', href = re.compile('/month_video.html\?'))
            dvd = BeautifulSoup(data, parseOnlyThese = dvdLink)
            dvdDate = self.parseDate(dvd.a.contents[0])
        except AttributeError:
            log.info('No DVD release info found.')

        # Does it have blu-ray release?
        bluray = []
        try:
            bees = SoupStrainer('b')
            soup = BeautifulSoup(data, parseOnlyThese = bees)
            bluray = soup.findAll('b', text = re.compile('Blu-ray'))
        except AttributeError:
            log.info('No Bluray release info found.')

        if dvdDate or theaterDate or bluray:
            dates = {
                'id': id,
                'dvd': dvdDate,
                'theater': theaterDate,
                'bluray': len(bluray) > 0
            }
            log.info('Found: %s', dates)
            return dates
        log.info('No release info found.')

    def parseDate(self, text, format = "%B %d, %Y"):

        try:
            date = int(time.mktime(time.strptime(text, "%B %d, %Y")))
        except ValueError:
            date = int(time.mktime(time.strptime(text, "%B %Y")))

        return date

    def getItems(self, data):

        results = []

        soup = BeautifulSoup(data)
        table = soup.find("table", { "class" : "chart" })

        try:
            for tr in table.findAll("tr"):
                item = {}

                for td in tr.findAll('td'):

                    # Get title and ID from <a>
                    if td.a and not td.a.img:
                        item['id'] = int(td.a['href'].split('/')[-1])
                        item['name'] = str(td.a.contents[0])

                    # Get year from <td>
                    if not td.h3 and not td.a:
                        if len(td.contents) == 1:
                            for y in td.contents:
                                try:
                                    item['year'] = int(y)
                                except ValueError:
                                    pass
                if item:
                    results.append(item)
        except AttributeError:
            log.error('No search results.')

        return results


def startEtaCron(debug):
    c = etaCron()
    c.debug = debug
    c.start()

    return c
