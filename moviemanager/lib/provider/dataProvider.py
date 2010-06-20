
from moviemanager.lib.provider.infoProvider import rssFeed
from string import ascii_letters, digits

class dataProvider(rssFeed):

    type = 'dataProvider'

    nameScores = [
        'proper:2', 'repack:2',
        'unrated:1',
        'x264:1',
        '720p:2', '1080p:2', 'dvd:1', 'dvdrip:1', 'bluray:2',
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

    def searchString(self, string):
        safe_chars = ascii_letters + digits + '_ '
        return ''.join([char if char in safe_chars else '' for char in string])

    def downloadLink(self, id):
        return self.downloadUrl % (id, self.getApiExt())

    def nfoLink(self, id):
        return self.nfoUrl % id

    def detailLink(self, id):
        return self.detailUrl % id

    def getApiExt(self):
        return ''
