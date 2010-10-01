from app.config.cplog import CPLog
from app.lib.provider.rss import rss
from imdb.parser.http.bsouplxml._bsoup import SoupStrainer, BeautifulSoup
from string import letters, digits
from urllib import urlencode
from urllib2 import URLError
import re
import urllib2

log = CPLog(__name__)

class HdTrailers(rss):

    apiUrl = 'http://www.hd-trailers.net/movie/%s/'
    backupUrl = 'http://www.hd-trailers.net/blog/'
    providers = ['apple.ico', 'yahoo.ico', 'moviefone.ico', 'myspace.ico', 'favicon.ico']

    def __init__(self, config):
        self.config = config

    def conf(self, value):
        return self.config.get('Trailer', value)

    def find(self, movie):

        url = self.apiUrl % self.movieUrlName(movie.name)
        log.info('Searching %s', url)

        try:
            data = urllib2.urlopen(url, timeout = self.timeout).read()
        except (IOError, URLError):
            log.error('Failed to open %s.' % url)
            return []

        p480 = []
        p720 = []
        p1080 = []
        didAlternative = False
        for provider in self.providers:
            results = self.findByProvider(data, provider)

            # Find alternative
            if results.get('404') and not didAlternative:
                results = self.findViaAlternative(movie.name)
                didAlternative = True

            p480.extend(results.get('480p'))
            p720.extend(results.get('720p'))
            p1080.extend(results.get('1080p'))

        return {'480p':p480, '720p':p720, '1080p':p1080}

    def findViaAlternative(self, movie):
        results = {'480p':[], '720p':[], '1080p':[]}

        arguments = urlencode({
            's':movie
        })
        url = "%s?%s" % (self.backupUrl, arguments)
        log.info('Searching %s', url)

        try:
            data = urllib2.urlopen(url, timeout = self.timeout).read()
        except (IOError, URLError):
            log.error('Failed to open %s.' % url)
            return results

        try:
            tables = SoupStrainer('div')
            html = BeautifulSoup(data, parseOnlyThese = tables)
            resultTable = html.findAll('h2', text = re.compile(movie))

            for h2 in resultTable:
                if 'trailer' in h2.lower():
                    parent = h2.parent.parent.parent
                    trailerLinks = parent.findAll('a', text = re.compile('480p|720p|1080p'))
                    try:
                        for trailer in trailerLinks:
                            results[trailer].insert(0, trailer.parent['href'])
                    except:
                        pass


        except AttributeError:
            log.debug('No trailers found in via alternative.')

        return results

    def findByProvider(self, data, provider):

        results = {'480p':[], '720p':[], '1080p':[]}
        try:
            tables = SoupStrainer('table')
            html = BeautifulSoup(data, parseOnlyThese = tables)
            resultTable = html.find('table', attrs = {'class':'bottomTable'})


            for tr in resultTable.findAll('tr'):
                trtext = str(tr).lower()
                if 'clips' in trtext:
                    break
                if 'trailer' in trtext and not 'clip' in trtext and provider in trtext:
                    nr = 0
                    resolutions = tr.findAll('td', attrs = {'class':'bottomTableResolution'})
                    #sizes = tr.findNext('tr').findAll('td', attrs = {'class':'bottomTableFileSize'})
                    for res in resolutions:
                        results[str(res.a.contents[0])].insert(0, res.a['href'])
                        #int(sizes[nr].contents[0].replace('MB', ''))
                        nr += 1

            return results

        except AttributeError:
            log.debug('No trailers found in provider %s.' % provider)
            results['404'] = True

        return results

    def movieUrlName(self, string):
        safe_chars = letters + digits + ' '
        r = ''.join([char if char in safe_chars else ' ' for char in string])
        name = re.sub('\s+' , '-', r).lower()

        try:
            int(name)
            return '-' + name
        except:
            return name
