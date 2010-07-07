from app.lib.provider.movie.base import movieBase
from imdb import IMDb
import logging
import urllib
import xml.etree.ElementTree as XMLTree

log = logging.getLogger(__name__)

class theMovieDb(movieBase):
    """Api for theMovieDb"""

    apiUrl = 'http://api.themoviedb.org/2.1'

    def __init__(self, config):
        log.info('Using TheMovieDb provider.')
        self.config = config
        
    def conf(self, option):
        return self.config.get('TheMovieDB', option)

    def find(self, q):
        ''' Find movie by name '''
        
        if self.isDisabled():
            return False
        
        log.info('TheMovieDB - Searching for movie: %s', q)

        url = "%s/%s/en/xml/%s/%s" % (self.apiUrl, 'Movie.search', self.conf('key'), urllib.quote_plus(self.toSaveString(q)))

        log.info('Search url: %s', url)

        data = urllib.urlopen(url)

        return self.parseXML(data)

    def findById(self, id):
        ''' Find movie by TheMovieDB ID '''
        
        if self.isDisabled():
            return False

        url = "%s/%s/en/xml/%s/%s" % (self.apiUrl, 'Movie.getInfo', self.conf('key'), id)
        data = urllib.urlopen(url)

        results = self.parseXML(data)

        return results.pop(0)

    def findByImdbId(self, id):
        ''' Find movie by IMDB ID '''
        
        if self.isDisabled():
            return False

        url = "%s/%s/en/xml/%s/%s" % (self.apiUrl, 'Movie.imdbLookup', self.conf('key'), id)
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

                    name = self.toSaveString(self.gettextelement(movie, "name"))
                    imdb = self.gettextelement(movie, "imdb_id")
                    year = str(self.gettextelement(movie, "released"))[:4]
                    
                    # do some IMDB searching if needed
                    if year == 'None' and imdb:
                        i = IMDb()
                        r = i.search_movie(name)
                        name = r[0]['title']
                        imdb = 'tt'+r[0].movieID
                        year = r[0]['year']

                    results.append(self.fillFeedItem(id, name, imdb, year))
                    
                    alternativeName = self.toSaveString(self.gettextelement(movie, "alternative_name"))
                    if alternativeName.lower() != name.lower():
                        results.append(self.fillFeedItem(id, alternativeName, imdb, year))

                log.info('TheMovieDB - Found: %s', results)
                return results
            except SyntaxError:
                log.error('TheMovieDB - Failed to parse XML response from TheMovieDb')
                return False
            
    def fillFeedItem(self, id, name, imdb, year):

        item = self.feedItem()
        item.id = id
        item.name = name
        item.imdb = imdb
        item.year = year
        
        return item
            
    def isDisabled(self):
        if self.conf('key') == '':
            log.error('TheMovieDB - No API key provided for TheMovieDB')
            True
        else:
            False
