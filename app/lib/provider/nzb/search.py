from app.lib.provider.nzb.sources.nzbs import nzbs
from app.lib.qualities import Qualities
import logging
import time

log = logging.getLogger(__name__)

class nzbSearcher():

    sources = []

    def __init__(self, config):

        self.config = config

        #config nzbs
        s = nzbs(config)
        self.sources.append(s)


    def find(self, movie, queue):
        ''' Find movie by name '''
        log.debug('Searching for movie: %s', movie.name)

        qualities = Qualities()

        for source in self.sources:

            results = []

            # find by main name
            type = queue.qualityType
            results.extend(source.find(movie, type, type))
            time.sleep(5)
            
            # Search for alternative naming
            for alt in qualities.getAlternatives(type):
                results.extend(source.find(movie, alt, type))
                time.sleep(5)

            if results:
                return results

        return {}

    def findById(self, id):
        ''' Find movie by TheMovieDB ID '''

        for source in self.sources:
            result = source.findById(id)
            if result:
                return result

        return []



    def findByImdbId(self, id):
        ''' Find movie by IMDB ID '''

        for source in self.sources:
            result = source.findByImdbId(id)
            if result:
                return result

        return []

