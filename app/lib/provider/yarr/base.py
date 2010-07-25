from app.lib.provider.rss import rss
from app.lib.qualities import Qualities
from urllib2 import URLError
import logging
import re
import time
import urllib2
log = logging.getLogger(__name__)

class nzbBase(rss):

    config = None
    type = 'nzb'
    name = ''

    nameScores = [
        'proper:2', 'repack:2',
        'unrated:1',
        'x264:1',
        '720p:2', '1080p:2', 'bluray:2', 'dvd:1', 'dvdrip:1', 'brrip:1', 'bdrip:1',
        'metis:1', 'diamond:1', 'wiki:1', 'CBGB:1',
        'german:-10', 'french:-10', 'spanish:-10', 'swesub:-20'
    ]

    catIds = {}
    catBackupId = ''

    available = True
    availableCheck = 0

    sizeGb = ['gb', 'gib']
    sizeMb = ['mb', 'mib']
    sizeKb = ['kb', 'kib']

    def parseSize(self, size):

        sizeRaw = size.lower()
        size = re.sub(r'[^0-9.]', '', size).strip()

        for s in self.sizeGb:
            if s in sizeRaw:
                return float(size) * 1024

        for s in self.sizeMb:
            if s in sizeRaw:
                return float(size)

        for s in self.sizeKb:
            if s in sizeRaw:
                return float(size) / 1024

        return 0

    def calcScore(self, nzb, movie):
        ''' Calculate the score of a NZB, used for sorting later '''

        score = 0
        if nzb.name:
            score = self.nameScore(nzb.name, movie)
            score += self.nameRatioScore(nzb.name, movie.name)

        return score

    def nameScore(self, name, movie):
        ''' Calculate score for words in the NZB name '''

        score = 0
        name = name.lower()

        #give points for the cool stuff
        for value in self.nameScores:
            v = value.split(':')
            add = int(v.pop())
            if v.pop() in name:
                score = score + add

        #points if the year is correct
        if str(movie.year) in name:
            score = score + 1

        return score

    def nameRatioScore(self, nzbName, movieName):

        nzbWords = re.split('\W+', self.toSearchString(nzbName).lower())
        movieWords = re.split('\W+', self.toSearchString(movieName).lower())

        # Replace .,-_ with space
        leftOver = len(nzbWords) - len(movieWords)
        if 2 <= leftOver <= 6:
            return 4
        else:
            return 0

    def isCorrectMovie(self, item, movie, qualityType):

        # Check for size first
        type = Qualities.types.get(qualityType)
        if type['minSize'] > item.size:
            log.debug('"%s" is to small to be %s. %sMB instead of the minimal of %sMB.' % (item.name, type['label'], item.size, type['minSize']))
            return False

        # Check if nzb contains imdb link
        if self.checkIMDB([item.content], movie.imdb):
            return True

        # if no IMDB link, at least check year range 1
        if len(movie.name.split(' ')) > 2 and self.correctYear([item.name], movie.year, 1) and self.correctName(item.name, movie.name):
            return True

        # if no IMDB link, at least check year
        if len(movie.name.split(' ')) == 2 and self.correctYear([item.name], movie.year, 0) and self.correctName(item.name, movie.name):
            return True

        return False

    def checkIMDB(self, haystack, imdbId):

        for string in haystack:
            if 'imdb.com/title/' + imdbId in string:
                return True

        return False

    def correctYear(self, haystack, year, range):

        for string in haystack:
            if str(year) in string or str(int(year) + range) in string or str(int(year) - range) in string: # 1 year of is fine too
                return True

        return False

    def correctName(self, nzbName, movieName):

        nzbWords = re.split('\W+', self.toSearchString(nzbName).lower())
        movieWords = re.split('\W+', self.toSearchString(movieName).lower())

        # Replace .,-_ with space
        found = 0
        for word in movieWords:
            if word in nzbWords:
                found += 1

        return found == len(movieWords)

    def getCatId(self, prefQuality):
        ''' Selecting category by quality '''

        for id, quality in self.catIds.iteritems():
            for q in quality:
                if q == prefQuality:
                    return id

        return self.catBackupId

    def downloadLink(self, id):
        return self.downloadUrl % (id, self.getApiExt())

    def nfoLink(self, id):
        return self.nfoUrl % id

    def detailLink(self, id):
        return self.detailUrl % id

    def getApiExt(self):
        return ''

    def isAvailable(self, testUrl):

        if self.availableCheck < time.time() - 900:
            self.availableCheck = time.time()
            try:
                urllib2.urlopen(testUrl, timeout = 30)
                self.available = True
            except (IOError, URLError):
                log.error('%s unavailable, trying again in an 15 minutes.' % self.name)
                self.available = False

        return self.available


class torrentBase(nzbBase):

    type = 'torrent'
