from moviemanager.lib.provider.movie.base import movieBase
from imdb import IMDb
import logging
import urllib
import xml.etree.ElementTree as XMLTree

log = logging.getLogger(__name__)

class theMovieDb(movieBase):
    """Api for theMovieDb"""

    apiUrl = 'http://api.themoviedb.org/2.1'
    apiKey = ''

    def __init__(self, config):
        log.info('Using TheMovieDb provider.')

        self.apiKey = config.get('key')

    def find(self, q):
        ''' Find movie by name '''
        
        if self.isDisabled():
            return False
        
        log.info('TheMovieDB - Searching for movie: %s', q)

        url = "%s/%s/en/xml/%s/%s" % (self.apiUrl, 'Movie.search', self.apiKey, urllib.quote_plus(q))

        log.info('Search url: %s', url)

        data = urllib.urlopen(url)

        return self.parseXML(data)

    def findById(self, id):
        ''' Find movie by TheMovieDB ID '''
        
        if self.isDisabled():
            return False

        url = "%s/%s/en/xml/%s/%s" % (self.apiUrl, 'Movie.getInfo', self.apiKey, id)
        data = urllib.urlopen(url)

        results = self.parseXML(data)

        return results.pop(0)

    def findByImdbId(self, id):
        ''' Find movie by IMDB ID '''
        
        if self.isDisabled():
            return False

        url = "%s/%s/en/xml/%s/%s" % (self.apiUrl, 'Movie.imdbLookup', self.apiKey, id)
        data = urllib.urlopen(url)

        results = self.parseXML(data)
        
        if results:
            return results.pop(0)
        else:
            return []

    def parseXML(self, data):
        if data:
            log.info('TheMovieDB - Parsing RSS')
            try:
                xml = XMLTree.parse(data).find("movies")

                results = []
                for movie in xml:
                    id = int(self.gettextelement(movie, "id"))

                    new = self.feedItem()
                    new.id = id
                    new.name = self.gettextelement(movie, "name")
                    new.imdb = self.gettextelement(movie, "imdb_id")
                    new.year = str(self.gettextelement(movie, "released"))[:4]
                    
                    # do some IMDB searching if needed
                    if new.year == 'None' and new.imdb:
                        i = IMDb()
                        r = i.search_movie(new.name)
                        new.name = r[0]['title']
                        new.imdb = 'tt'+r[0].movieID
                        new.year = r[0]['year']

                    results.append(new)

                log.info('TheMovieDB - Found: %s', results)
                return results
            except SyntaxError:
                log.error('TheMovieDB - Failed to parse XML response from TheMovieDb')
                return False
            
    def isDisabled(self):
        if self.apiKey == '':
            log.error('TheMovieDB - No API key provided for TheMovieDB')
            True
        else:
            False
