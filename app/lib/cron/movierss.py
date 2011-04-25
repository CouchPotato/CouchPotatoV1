from app import latinToAscii
from app.config.cplog import CPLog
from app.config.db import RenameHistory, Session as Db
from app.controllers.movie import MovieController
from app.lib.cron.base import cronBase
from app.lib.library import Library
from app.lib.provider.rss import rss

from xmg import xmg
import cherrypy
import os
import re
import shutil
import time
import traceback


log = CPLog(__name__)

class MovieRSSCron(cronBase, Library, rss):

    ''' Cronjob for getting blu-ray.com releases '''

    lastChecked = 0
    intervalSec = 86400
    config = {}
    MovieRSSUrl = "http://www.blu-ray.com/rss/newreleasesfeed.xml"

    def conf(self, option):
        return
#        return self.config.get('MovieRSS', option)

    def run(self):
        log.info('Movie RSS thread is running.')

        wait = 0.1 if self.debug else 5

        time.sleep(10)
        while True and not self.abort:
            now = time.time()
            if (self.lastChecked + self.intervalSec) < now:
                try:
                    self.running = True
                    self.lastChecked = now
                    self.doRSSCheck()
                    self.running = False
                except Exception as exc:
                    log.error("!!Uncought exception in movie RSS thread.")
                    log.error(traceback.format_exc())
            time.sleep(wait)

        log.info('Movie RSS has shutdown.')

    def isDisabled(self):

        #if (self.conf('enabled'):
            
            return False
        #else:

        #    return True

    def doRSSCheck(self):
        '''
        Go find movies and add them!
        '''

        log.info('Starting Movies RSS check')

        if self.isDisabled():
            log.info('Movie RSS has been disabled')
            return

        if not self.isAvailable(self.MovieRSSUrl):
            log.info('Movie RSS is not available')
            return

        RSSData = self.urlopen(self.MovieRSSUrl)
        RSSItems = self.getItems(RSSData)
        
        RSSMovies = []
        RSSMovie = {'name': 'test', 'year' : '2009'}
        
        MyMovieController = MovieController()
                        
        for RSSItem in RSSItems:
            RSSMovie['name'] = self.gettextelement(RSSItem, "title").lower().split("blu-ray")[0].strip("(").rstrip() #strip Blu-ray and spaces
            RSSMovie['year'] = self.gettextelement(RSSItem, "description").split("|")[1].strip("(").strip() #find movie year in description
            
            if RSSMovie['name'].find("/") == -1: # make sure it is not a double movie release 
                alreadyfound = False
                for test in RSSMovies:
                    if test.values() == RSSMovie.values(): # make sure we did not already include it...
                        alreadyfound = True
                if not alreadyfound:                
                    log.info('Movie found: %s' % RSSMovie)
                    RSSMovies.append(RSSMovie.copy())
                
        if not RSSMovies:
            return
            
        log.info("Ready to add movies to the wanted list.")

        for RSSMovie in RSSMovies:
            if self.abort:
                return
            log.info('Searching for "%s".' % RSSMovie['name'])
            try:
                result = cherrypy.config['searchers']['movie'].find(RSSMovie['name'] + ' ' + RSSMovie['year'], limit = 1)
                if result:
                    imdbmovie = cherrypy.config['searchers']['movie'].sources[1].findByImdbId(result.imdb, True)
                    if imdbmovie['kind'] == 'movie':
                        log.info('Found: %s ' % imdbmovie['title'] + ' year: ' + str(imdbmovie['year']) + ' Rating: ' + str(imdbmovie['rating']))
                        if float(imdbmovie['rating']) > 5.45 and imdbmovie['year'] > 2008:
                            log.info('ADDING!!!')
                            MyMovieController._addMovie(result, 8)
                    else:
                        log.info('This is not a movie!')
                else:
                    log.info('Movie not found :(')
            except:
                log.info('Something strange happenend with %s' % RSSMovie['name'])

def startMovieRSSCron(config, searcher, debug):
    cron = MovieRSSCron()
    cron.config = config
    cron.searcher = searcher
    cron.debug = debug
    cron.start()

    return cron
