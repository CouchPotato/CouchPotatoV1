
from app.lib.provider.rss import rss
import re

class nzbBase(rss):

    type = 'nzb'

    nameScores = [
        'proper:2', 'repack:2',
        'unrated:1',
        'x264:1',
        '720p:2', '1080p:2', 'bluray:2', 'dvd:1', 'dvdrip:1', 'brrip:1', 'bdrip:1',
        'metis:1', 'diamond:1', 'wiki:1', 'CBGB:1'
    ]

    def calcScore(self, nzb, movie):
        ''' Calculate the score of a NZB, used for sorting later '''

        score = 0
        if nzb.name:
            score = self.nameScore(nzb.name, movie)

        return score

    def nameScore(self, name, movie):
        ''' Calculate score for words in the NZB name '''
        
        score = 0
        
        #give points for the cool stuff
        for value in self.nameScores:
            v = value.split(':')
            add = int(v.pop())
            if v.pop() in name.lower():
                score = score + add
        
        #points if the year is correct
        if str(movie.year) in name:
            score = score + 1

        return score
    
    def isCorrectMovie(self, item, movie):
        
        # Check if nzb contains imdb link
        if self.checkIMDB([item.content], movie.imdb):
            return True
        
        # if no IMDB link, at least check year
        if self.correctYear([item.name], movie.year) and self.correctName(item.name, movie.name):
            return True
        
        return False
        
    def checkIMDB(self, haystack, imdbId):
        
        for string in haystack:
            if 'imdb.com/title/'+imdbId in string:
                return True
        
        return False
        
    def correctYear(self, haystack, year):
        
        for string in haystack:
            if str(year) in string or str(int(year)+1) in string or str(int(year)-1) in string: # 1 year of is fine too
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
    
    def downloadLink(self, id):
        return self.downloadUrl % (id, self.getApiExt())

    def nfoLink(self, id):
        return self.nfoUrl % id

    def detailLink(self, id):
        return self.detailUrl % id

    def getApiExt(self):
        return ''


class torrentBase(nzbBase):

    type = 'torrent'