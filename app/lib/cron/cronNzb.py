from app.config.db import Movie, Session as Db
from app.lib.cron.cronBase import cronBase
from sqlalchemy.sql.expression import or_
import cherrypy
import logging
import os
import time
import urllib

log = logging.getLogger(__name__)

class NzbCron(cronBase):

    ''' Cronjob for searching for NZBs '''

    lastChecked = 0
    provider = None
    sabNzbd = None
    intervalSec = 10
    checkTheseMovies = []

    def run(self):
        log.info('NzbCron thread is running.')

        self.setInterval(self.config.get('Intervals', 'nzb'))
        self.forceCheck()
        
        if not self.debug:
            time.sleep(10)
            
        wait = 0.1 if self.debug else 1
        while True and not self.abort:

            #check single movie
            for movie in self.checkTheseMovies:
                self._searchNzb(movie)
                self.checkTheseMovies.pop(0)
                #log.info('Sleeping search for 5 sec')
                time.sleep(5)

            #check all movies
            now = time.time()
            if (self.lastChecked + self.intervalSec) < now and not self.debug:
                self.lastChecked = now
                self.searchNzbs()

            #log.info('Sleeping NzbCron for %d seconds' % 10)
            time.sleep(wait)

        log.info('NzbCron has shutdown.')

    def setInterval(self, interval):
        self.intervalSec = int(interval) * 60 * 60

    def forceCheck(self, movie = None):
        if movie == None:
            self.lastChecked = time.time() - self.intervalSec # + 10
        else:
            self.checkTheseMovies.append(movie)

    def searchNzbs(self):
        log.info('Searching for NZB.')
        self.doCheck()

        #get all wanted movies
        movies = Db.query(Movie).filter(or_(Movie.status == 'want', Movie.status == 'waiting')).all()
        for movie in movies:
            if not self.abort:
                self._searchNzb(movie)

        self.doCheck(False)
        log.info('Finished search.')


    def _searchNzb(self, movie):

        for queue in movie.queue:

            # Movie already found, don't search further 
            if queue.completed:
                log.debug('%s already completed. Not searching for any qualities below.' % queue.qualityType)
                return True

            # only search for active and not completed
            if queue.active and not queue.completed and not self.abort:

                results = self.provider.find(movie, queue)

                #search for highest score
                highest = None
                highestScore = 0
                for result in results:
                    if result.score > highestScore:
                        # Wait for download if complete = false
                        highest = result
                        highestScore = result.score

                #send highest to SABnzbd & mark as snatched
                if highest:

                    #update what I found
                    queue.name = highest.name
                    queue.link = highest.detailUrl

                    waitFor = queue.waitFor * (60 * 60 * 24)

                    if queue.markComplete or (not queue.markComplete and result.date + waitFor < time.time()):
                        if self.config.get('NZB', 'sendTo') == 'Sabnzbd':
                            success = self.sabNzbd.send(highest)
                        else:
                            success = self.blackHole(highest)
                    else:
                        success = False
                        log.info('Found %s but waiting for %d hours.' % (result.name, ((result.date + waitFor) - time.time()) / (60 * 60)))

                    # Set status
                    if success:
                        if queue.markComplete:
                            movie.status = u'snatched'
                        else:
                            movie.status = u'waiting'

                        queue.completed = True

                    return True
                time.sleep(5)

        return False
    
    def blackHole(self, nzb):
        blackhole = self.config.get('NZB', 'blackhole')
        if not blackhole or not os.path.isdir(blackhole):
            log.error('No directory set for blackhole download.')
        else:
            fullPath = os.path.join(blackhole, nzb.name+'.nzb')
            
            if not os.path.isfile(fullPath):
                log.info('Downloading NZB to %s.' % fullPath)
                file = urllib.urlopen(nzb.url).read()
                with open(fullPath, 'w') as f:
                    f.write(file)
                
                return True
            else:
                log.error('File %s already exists.' % fullPath)

        return False

    def doCheck(self, bool = True):
        self.running = bool
        self.lastChecked = time.time()

    def isChecking(self):
        return self.running

    def lastCheck(self):
        return self.lastChecked

    def nextCheck(self):

        t = (self.lastChecked + self.intervalSec) - time.time()

        s = ''
        tm = time.gmtime(t)
        if tm.tm_hour > 0:
            s += '%d hours' % tm.tm_hour
        if tm.tm_min > 0:
            s += ' %d minutes' % tm.tm_min
        if tm.tm_sec > 0 and not tm.tm_hour > 0 and not tm.tm_min > 15:
            s += ' %d seconds' % tm.tm_sec

        return {
            'timestamp': t,
            'string': s
        }

def startNzbCron(config, debug):
    cron = NzbCron()
    cron.config = config
    cron.debug = debug
    cron.start()

    return cron
