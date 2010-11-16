from app.core import getLogger
from app.lib.bones import PluginBones
from app.lib.rss import Rss
from library.imdb import IMDb

import re
import uuid
import datetime
import shelve
import time

log = getLogger(__name__)

class imdb(PluginBones, Rss):
    """API wrapper for IMDB"""

    def _identify(self):
        return uuid.UUID('56d34817-cd5f-473b-a7c4-d835e191a5ce')

    def postConstruct(self):
        #MovieBase.__init__(self, config)
        self._loadConfig(self.name)

        self.p = IMDb()

        self._listen('findMovie', self.find)
        self._listen('getMovieInfo', self.findInfo)

    def _getDependencies(self):
        #@todo: implement dependencies
        return {}


    def find(self, e, config):
        ''' Find movie by name '''

        q = unicode(e._kwargs.get('q'))
        limit = e._kwargs.get('limit' , 8)

        log.info("IMDB - Searching for movie: " + q)

        searchResults = self.p.search_movie(q)
        results = self.toResults(searchResults, limit)

        # Add the results to the event item
        log.info('Found %s.' % results)
        e.addResults(results)

    def findInfo(self, id):
        ''' Find movie info by IMDB ID '''

        log.info('IMDB - Searching for movie: %s', str(id))

        searchResults = self.p.get_movie(id.replace('tt', ''))
        result = self.toResult(searchResults)

        log.info('Found %s.' % result)
        return result

    def toResults(self, results, limit = 8):
        limitedResults = results[:limit]
        return [self.toResult(movie) for movie in limitedResults]

    def toResult(self, r):

        new = self.feedItem()
        new.imdb = 'tt' + r.movieID
        new.name = r['title']
        new.year = r['year']

        return new

    def getInfo(self):
        return {
            'name' : 'IMDB Provider',
            'author' : 'Ruud & alshain',
            'version' : '0.1'
        }

class ImdbInfo():
    def __init__(self):
        self.imdbpy = self.getImdbpy()
        self.cachefile = "imdb_cache.db"
        self.expirationTime = datetime.timedelta(days=30)
        self._ = time.clock()

    def fetchCache(self, imdbid):
        #TODO: Implement plugin-based caching mechanism
        self.fcopenstartclock = time.clock()
        cache = shelve.open(self.cachefile)

        if cache.has_key(imdbid):
            movie = cache[imdbid]
            if movie['cachedTime'] > datetime.datetime.now() - self.expirationTime:
                cache.close()
                return movie

        cache.close()

    def putCache(self, movie):
        cacheTime = datetime.datetime.now()
        movie['cachedTime'] = cacheTime

        cache = shelve.open(self.cachefile)
        cache[movie['imdbid']] = movie
        cache.close()

    def _getMovie(self, imdbid):
        movie = self.imdbpy.get_movie(imdbid.replace('tt', ''))
        self.imdbpy.update(movie)
        self.imdbpy.update(movie, info=('release dates', 'taglines', 'dvd'))
        return movie

    def _strList(self, objList):
        return [str(x) for x in objList]

    def getImdbpy(self, access = 'http', module = 'beautifulsoup'):
        return IMDb(access, useModule =  module)

    def getInfo(self, imdbid):
        imdbid = str(imdbid).replace('tt', '')
        isCached = self.fetchCache(imdbid)

        if not isCached:
            movie = self._getMovie(imdbid)
        else:
            return isCached

        movieInfo = {   'title': self.title(movie),
                        'titles': self.titles(movie),
                        'alternateTitles': self.alternateTitles(movie),
                        'mpaa': self.mpaa(movie),
                        'cast': self.cast(movie),
                        'director': self.director(movie),
                        'genres': self.genres(movie),
                        'kind': self.kind(movie),
                        'plot': self.plot(movie),
                        'plotOutline': self.plotOutline(movie),
                        'producer': self.producer(movie),
                        'imdbRating': self.imdbRating(movie),
                        'runtimes': self.runtimes(movie),
                        'top250': self.top250(movie),
                        'imdbVotes': self.imdbVotes(movie),
                        'writers': self.writers(movie),
                        'year': self.year(movie),
                        'taglines': self.taglines(movie),
                        'releaseDates': self.releaseDates(movie),
                        'dvdReleases': self.dvdReleases(movie),
                        'imdbid': imdbid}
        self.putCache(movieInfo)
        return movieInfo

    def titles(self, movie):
        ''' Return all titles that imdb knows about for this movie.
        '''
        titleKeys = [x for x in movie.keys() if 'title' in x.lower()]
        titles = []
        for key in titleKeys:
            titles.append(movie[key])

        return titles

    def alternateTitles(self, movie):
        ''' Title translations for releases in other countries.
        '''
        if movie.has_key('akas'):
            titles = {}
            for aka in movie['akas']:
                splitted = [x for x in aka.split("::") if x != '']
                if len(splitted) > 1:
                    titles[splitted[0]] = splitted[1]
                else:
                    titles[splitted[0]] = None

            return titles

    def dvdReleases(self, movie):
        if movie.has_key('dvd'):
            dvds = []
            for dvd in movie['dvd']:
                dvd['release date'] = datetime.datetime.strptime(dvd['release date'], '%Y-%m-%d')
                dvds.append(dvd)
            return dvds

    def taglines(self, movie):
        return movie.get('taglines')

    def releaseDates(self, movie):
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        if movie.has_key('runtimes'):
            rDates = {}
            for releaseDate in movie['release dates']:
                search = re.search(r"(?P<country>\w+)::(?P<date>\d{1,2} \w+ \d\d\d\d)( (?P<note>\(.*\)))?", releaseDate)
                if search:
                    country, date, note = search.group('country', 'date', 'note')
                    day, month, year = date.split()
                    month = months.index(month) + 1
                    date = datetime.date(int(year), int(month), int(day))
                    dn = {'date': date, 'note': note}
                    if country not in rDates:
                        rDates[country] = [dn]
                    else:
                        if dn not in rDates[country]:
                            rDates[country].append(dn)
            return rDates

    def title(self, movie):
        ''' Return the main title for this movie according to IMDb
        '''
        return movie.get('title')

    def mpaa(self, movie):
        if movie.has_key('mpaa'):
            #If it exists, this key from imdbpy is the best way to get MPAA movie rating
            rating_match = re.search(r"Rated (?P<rating>[a-zA-Z0-9-]+)", movie['mpaa'])
            if rating_match:
                rating = rating_match.group('rating')
                return rating

        if movie.has_key('certificates'):
            #IMDB lists all the certifications a movie has gotten the world over.
            #Each movie often has multiple certifications per country since it
            #will often get re-rated for different releases (theater and
            #then DVD for example).

            #for movies with multiple certificates, we pick the 'lowest' one since
            #MPAA ratings are more permissive the more recent they were given.
            #A movie that was rated R in the 70s may be rated PG-13 now but will
            #probably never be rerated NC-17 .
            ratings_list_ordered = ['G', 'PG', 'PG-13', 'R', 'NC-17', 'Unrated']

            #Map older rating types to their modern equivalents
            ratings_mappings = {'M':'NC-17',
                                'X':'NC-17',
                                'GP':'PG',
                                'Approved': 'PG',
                                'Open': 'PG',
                                'Not Rated': 'Unrated'
                                }

            certs = movie['certificates']
            good_ratings = []
            for cert in certs:
                if 'usa' in cert.lower():
                    rating_match = re.match(r"USA:(?P<rating>[ a-zA-Z0-9-]+)", cert)
                    if rating_match:
                        rating = rating_match.group('rating')
                        if rating in ratings_list_ordered:
                            index = ratings_list_ordered.index(rating)
                            if index not in good_ratings:
                                good_ratings.append(index)
                        elif rating in ratings_mappings:
                            index = ratings_list_ordered.index(ratings_mappings[rating])
                            if index not in good_ratings:
                                good_ratings.append(index)

            if good_ratings:
                best_rating = ratings_list_ordered[min(good_ratings)]
                return best_rating

    def cast(self, movie):
        '''Returns a list of people names or None
       '''
        if movie.has_key('cast'):
            return self._strList(movie['cast'])

    def director(self, movie):
        '''Returns a list of people names or None
       '''
        if movie.has_key('director'):
            return self._strList(movie['director'])

    def genres(self, movie):
        '''Returns a list of genres or None
       '''
        return movie.get('genres')

    def kind(self, movie):
        return movie.get('kind')

    def plot(self, movie):
        if movie.has_key('plot'):
            plot = movie['plot'][0]
            return plot.split("::")[0]

    def plotOutline(self, movie):
        return movie.get('plot outline')

    def producer(self, movie):
        '''Returns a list of people names or None
       '''
        if movie.has_key('producer'):
            return self._strList(movie['producer'])

    def imdbRating(self, movie):
        return movie.get('rating')

    def runtimes(self, movie):
        """Returns a list of tuples like this:

        [(105, {'country': u'Canada', 'notes': u'Toronto International Film Festival'}),
        (108, {'country': u'Hong Kong', 'notes': None}),
        (105, {'country': u'USA', 'notes': None}),
        (104, {'country': None, 'notes': u'director's cut'}),
        (100, {'country': u'Spain', 'notes': u'DVD edition'})]

        """
        if movie.has_key('runtimes'):
           times = []
#           import pdb; pdb.set_trace()
           for runtime in movie['runtimes']:
               try:
                   #imdbpy usually returns a runtime with no country or notes, so we'll catch that instance
                   time = int(runtime)
                   times.append((time, {}))
               except ValueError:
                   splitted = [x for x in runtime.split(":") if x != '']
                   notes = None
                   country = None
                   for split in splitted:
                       try:
                           time = int(split)
                           continue
                       except:
                           if split[0] == "(" and split[-1] == ")":
                               notes = split[1:-1]
                               continue
                           if re.match("\w+", split):
                               country = split
                   times.append((time, {'country': country, 'notes': notes}))

           return times

    def top250(self, movie):
       ''' Returns the movies rank in the IMDB top250 if it is ranked
       '''
       return movie.get('top 250 rank')

    def imdbVotes(self, movie):
       '''Returns the number of votes the movie has received on imdb
       '''
       return movie.get('votes')

    def writers(self, movie):
       if movie.has_key('writer'):
           return self._strList(movie['writer'])

    def year(self, movie):
       return movie.get('year')


