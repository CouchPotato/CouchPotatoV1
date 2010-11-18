from app.core import getLogger
from app.lib.bones import PluginBones
from app.lib.rss import Rss
from library.imdb import IMDb

import re
import uuid
import datetime
import shelve
import operator

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

class ImdbParser():
    ''' Parses Movie() objects from IMDBpy
    '''
    def _strList(self, objList):
        ''' Stringifies every object in objList and returns the list of strings
        '''
        return [str(x) for x in objList]

    def getAllTitles(self, imdbMovie):
        ''' Return a list of every possible thing this movie could be called.
        This includes the official title,
        '''
        titles = [imdbMovie['title']]

        titles.extend(self.titles(imdbMovie))
        akas = self.alternateTitles(imdbMovie)
        if akas:
            titles.extend(akas.keys())

        #return a de-duplicated list of titles
        return list(dict.fromkeys(titles))

    def titles(self, imdbMovie):
        ''' Return all titles that imdb knows about for this movie.
        Specifically, this is usually just the various titles that IMDb uses, like "The Matrix" and "The Matrix (1999)"
        '''
        titleKeys = [x for x in imdbMovie.keys() if 'title' in x.lower()]
        titles = []
        for key in titleKeys:
            titles.append(imdbMovie[key])

        return list(dict.fromkeys(titles))

    def alternateTitles(self, imdbMovie):
        ''' Title translations for releases in other countries.
        '''
        if imdbMovie.has_key('akas'):
            titles = {}
            for aka in imdbMovie['akas']:
                splitted = [x for x in aka.split("::") if x != '']
                if len(splitted) > 1:
                    titles[splitted[0]] = splitted[1]
                else:
                    titles[splitted[0]] = None

            return titles

    def dvdReleases(self, imdbMovie):
        ''' Returns a dict of various dvd releases for the movie with their release dates
        '''
        if imdbMovie.has_key('dvd'):
            dvds = []
            for dvd in imdbMovie['dvd']:
                dvd['release date'] = datetime.datetime.strptime(dvd['release date'], '%Y-%m-%d')
                dvds.append(dvd)
            return dvds

    def taglines(self, imdbMovie):
        ''' Returns the movies taglines.  Here's some taglines for The Matrix:
        http://www.imdb.com/title/tt0133093/taglines
        '''
        return imdbMovie.get('taglines')

    def releaseDates(self, imdbMovie):
        ''' Returns a dict of release dates.  Each key is a country and each value is a list of the various dates the
        movie was released in that country.
        '''
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        if imdbMovie.has_key('runtimes'):
            rDates = {}
            for releaseDate in imdbMovie['release dates']:
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

    def title(self, imdbMovie):
        ''' Return the main title for this movie according to IMDb
        '''
        return imdbMovie.get('title')

    def mpaa(self, imdbMovie):
        ''' Returns the MPAA rating for the movie, if available.
        '''
        #TODO: This should probably be a method that takes a country and returns the rating for that country
        if imdbMovie.has_key('mpaa'):
            #If it exists, this key from imdbpy is the best way to get MPAA movie rating
            rating_match = re.search(r"Rated (?P<rating>[a-zA-Z0-9-]+)", imdbMovie['mpaa'])
            if rating_match:
                rating = rating_match.group('rating')
                return rating

        if imdbMovie.has_key('certificates'):
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

            certs = imdbMovie['certificates']
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

    def cast(self, imdbMovie):
        '''Returns a list of people names or None
       '''
        if imdbMovie.has_key('cast'):
            return self._strList(imdbMovie['cast'])

    def director(self, imdbMovie):
        '''Returns a list of people names or None
       '''
        if imdbMovie.has_key('director'):
            return self._strList(imdbMovie['director'])

    def genres(self, imdbMovie):
        '''Returns a list of genres or None
       '''
        return imdbMovie.get('genres')

    def kind(self, imdbMovie):
        return imdbMovie.get('kind')

    def plot(self, imdbMovie):
        if imdbMovie.has_key('plot'):
            plot = imdbMovie['plot'][0]
            return plot.split("::")[0]

    def plotOutline(self, imdbMovie):
        return imdbMovie.get('plot outline')

    def producer(self, imdbMovie):
        '''Returns a list of people names or None
       '''
        if imdbMovie.has_key('producer'):
            return self._strList(imdbMovie['producer'])

    def imdbRating(self, imdbMovie):
        return imdbMovie.get('rating')

    def runtimes(self, imdbMovie):
        """Returns a list of tuples like this:

        [(105, {'country': u'Canada', 'notes': u'Toronto International Film Festival'}),
        (108, {'country': u'Hong Kong', 'notes': None}),
        (105, {'country': u'USA', 'notes': None}),
        (104, {'country': None, 'notes': u'director's cut'}),
        (100, {'country': u'Spain', 'notes': u'DVD edition'})]

        """
        if imdbMovie.has_key('runtimes'):
           times = []
#           import pdb; pdb.set_trace()
           for runtime in imdbMovie['runtimes']:
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

    def top250(self, imdbMovie):
       ''' Returns the movies rank in the IMDB top250 if it is ranked, else None
       '''
       return imdbMovie.get('top 250 rank')

    def imdbVotes(self, imdbMovie):
       '''Returns the number of votes the movie has received on imdb
       '''
       return imdbMovie.get('votes')

    def writers(self, imdbMovie):
        ''' Returns a list of people names
        '''
        if imdbMovie.has_key('writer'):
            return self._strList(imdbMovie['writer'])

    def year(self, imdbMovie):
       return imdbMovie.get('year')

class ImdbWonders(ImdbParser):
    ''' General front-end to IMDBpy.
    '''
    def __init__(self):
        self.imdbpy = self.getImdbpy()
        self.cachefile = "imdb_cache.db"
        self.defaultExpTime= datetime.timedelta(days=30)
        self.imdbpyRequiredInfo = ['main', 'plot', 'release dates', 'akas', 'taglines', 'dvd']

    def getImdbpy(self, access = 'http', module = 'beautifulsoup'):
        ''' Returns an IMDb() object
        '''
        return IMDb(access, useModule =  module)

    def searchMovie(self, text):
        ''' Returns a list of movie dicts as returned by self.buildInfo().  These are sparsely populated dicts with
        just a minimum amount of info mainly including titles and year.

        After selecting a result, pass it to self.expandInfo() to get the rest of the information.
        '''
        results = self.fetchCache(text.lower())
        if results:
            return results

        searchResults = self.imdbpy.search_movie(text)
        imdbpyMatches = []
        for result in searchResults:
            if 'movie' in result['kind']:
                titles = self.getAllTitles(result)
                for title in titles:
                    if title.lower() == text.lower():
                        imdbpyMatches.append(result)

        exactMatch = []
        subMatch = []
        superMatch = []
        otherMatch = []
        for match in imdbpyMatches:
            if match['title'].lower() == text.lower():
                exactMatch.append(match)
            elif match['title'].lower() in text.lower():
                subMatch.append(match)
            elif text.lower() in match['title'].lower():
                superMatch.append(match)
            else:
                otherMatch.append(match)

        exactMatch.sort(key = operator.itemgetter("title", "year"), reverse=True)
        subMatch.sort(key = operator.itemgetter("title", "year"), reverse=True)
        superMatch.sort(key = operator.itemgetter("title", "year"), reverse=True)
        otherMatch.sort(key = operator.itemgetter("title", "year"), reverse=True)

        sortedMatches = exactMatch
        sortedMatches.extend(subMatch)
        sortedMatches.extend(superMatch)
        sortedMatches.extend(otherMatch)

        resultset = [self.buildInfo(movie) for movie in sortedMatches]
        self.putCache(resultset, text.lower(), datetime.timedelta(days=1))

        return resultset

    def fetchCache(self, key):
        ''' Return cached info or None if it's not cached or expired
        '''
        #TODO: Implement plugin-based caching mechanism
        cache = shelve.open(self.cachefile)

        if cache.has_key(key):
            cachedObj = cache[key]
            if cachedObj['_cachedTime'] > datetime.datetime.now() - cachedObj['_expiration']:
                cache.close()
                return cachedObj['data']

        cache.close()

    def putCache(self, obj, key, expiration = None):
        ''' Puts item into the cache.

        'key' will be the key to access the item from the cache
        'expiration' should be a datetime.timedelta, which defaults to self.defaultExpTime
        '''
        if not expiration:
            expiration = self.defaultExpTime

        cacheMe = {'_cachedTime': datetime.datetime.now(), '_expiration': expiration, 'data': obj}

        cache = shelve.open(self.cachefile)
        cache[key] = cacheMe
        cache.close()

    def _getMovie(self, imdbid):
        ''' Returns an imdbpy Movie() object for imdbid that has been updated with the info required
            for self.getInfo()
        '''
        movie = self.imdbpy.get_movie(imdbid.replace('tt', ''))
        self._updateMovie(movie)
        return movie

    def _updateMovie(self, imdbMovie):
        needToGet = []
        for info in self.imdbpyRequiredInfo:
            if info not in imdbMovie.current_info:
                needToGet.append(info)
        if needToGet:
            self.imdbpy.update(imdbMovie, info=needToGet)

        return imdbMovie

    def getInfo(self, imdbid):
        ''' Returns movie information via self.buildInfo() or via a cached version if available.
        '''
        imdbid = str(imdbid).replace('tt', '')
        isCached = self.fetchCache(imdbid)

        if not isCached:
            #movie isn't cached so go get it from IMDb
            movie = self._getMovie(imdbid)
        else:
            return isCached

        movieInfo = self.buildInfo(movie)

        #Since movie isn't cached, cache it
        self.putCache(movieInfo, imdbid)
        return movieInfo

    def buildInfo(self, imdbMovie):
        ''' Build a sanitized and useful dict of information about the IMDb.Movie() object
        '''
        movieInfo = {   'title': self.title(imdbMovie),
                        'titles': self.titles(imdbMovie),
                        'alternateTitles': self.alternateTitles(imdbMovie),
                        'mpaa': self.mpaa(imdbMovie),
                        'cast': self.cast(imdbMovie),
                        'director': self.director(imdbMovie),
                        'genres': self.genres(imdbMovie),
                        'kind': self.kind(imdbMovie),
                        'plot': self.plot(imdbMovie),
                        'plotOutline': self.plotOutline(imdbMovie),
                        'producer': self.producer(imdbMovie),
                        'imdbRating': self.imdbRating(imdbMovie),
                        'runtimes': self.runtimes(imdbMovie),
                        'top250': self.top250(imdbMovie),
                        'imdbVotes': self.imdbVotes(imdbMovie),
                        'writers': self.writers(imdbMovie),
                        'year': self.year(imdbMovie),
                        'taglines': self.taglines(imdbMovie),
                        'releaseDates': self.releaseDates(imdbMovie),
                        'dvdReleases': self.dvdReleases(imdbMovie),
                        'imdbid': self.imdbpy.get_imdbID(imdbMovie),
                        '_infosets': imdbMovie.current_info
                        }

        return movieInfo

    def expandInfo(self, imdbInfo):
        ''' Takes an info dict as built by self.buildInfo and adds additional infosets to it if it was built
        with a movie object not containg all necessary imdbpy infosets.
        '''
        for info in self.imdbpyRequiredInfo:
            if info not in imdbInfo['_infosets']:
                return self.getInfo(imdbInfo['imdbid'])

        return imdbInfo