from app.lib.provider.movie.base import movieBase
import logging
import sha
import urllib
import xml.etree.ElementTree as XMLTree

log = logging.getLogger(__name__)

class sceneReleases(movieBase):

    feedUrl = 'http://scenereleases.info/category/movies/feed'

    def checkForNew(self):
        ''' Find movie by name '''

        if self.isDisabled():
            return False

        log.info('SceneReleases - Searching for new released movies.')
        data = urllib.urlopen(self.feedUrl)

        return self.parseXML(data)

    def alreadyChecked(self, name):
        ''' Do some checking, to prevent double feeding '''


        return False

    def parseXML(self, data):
        if data:
            log.info('SceneReleases - Parsing RSS')
            try:
                xml = XMLTree.parse(data).find("channel/item")

                results = []
                for movie in xml:
                    name = self.gettextelement(movie, "title")
                    id = sha.new(title).digesthex()

                    new = self.feedItem()
                    new.id = id
                    new.name = name
                    new.imdb = self.gettextelement(movie, "imdb_id")
                    new.year = str(self.gettextelement(movie, "released"))[:4]

                    results.append(new)

                log.info('TheMovieDB - Found: %s', results)
                return results
            except SyntaxError:
                log.error('TheMovieDB - Failed to parse XML response from TheMovieDb')
                return False

    def findImdbRating(self, string):

        return rating

