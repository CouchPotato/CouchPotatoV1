from app.config.db import Movie, Session as Db
from app.lib.cron.cronBase import cronBase
from sqlalchemy.sql.expression import or_
import datetime
import logging
import os
import time
import urllib

log = logging.getLogger(__name__)

class YarrCron(cronBase):

    ''' Cronjob for searching for nzb/torrents '''

    lastChecked = 0
    provider = None
    sabNzbd = None
    intervalSec = 10
    checkTheseMovies = []

    def run(self):
        log.info('YarrCron thread is running.')

        self.setInterval(self.config.get('Intervals', 'search'))
        self.forceCheck()

        if not self.debug:
            time.sleep(10)

        wait = 0.1 if self.debug else 1
        while True and not self.abort:

            #check single movie
            for movie in self.checkTheseMovies:
                self._search(movie)
                self.checkTheseMovies.pop(0)

            #check all movies
            now = time.time()
            if (self.lastChecked + self.intervalSec) < now: # and not self.debug:
                self.lastChecked = now
                self.searchAll()

            time.sleep(wait)

        log.info('YarrCron has shutdown.')

    def setInterval(self, interval):
        self.intervalSec = int(interval) * 60 * 60

    def forceCheck(self, movie = None):
        if movie == None:
            self.lastChecked = time.time() - self.intervalSec # + 10
        else:
            self.checkTheseMovies.append(movie)

    def searchAll(self):
        log.info('Searching for new download for all movies.')
        self.doCheck()

        #get all wanted movies
        movies = Db.query(Movie).filter(or_(Movie.status == 'want', Movie.status == 'waiting')).all()
        for movie in movies:
            if not self.abort:
                self._search(movie)

        self.doCheck(False)
        log.info('Finished search.')


    def _search(self, movie):

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
                        highest = result
                        highestScore = result.score

                #send highest to SABnzbd & mark as snatched
                if highest:

                    #update what I found
                    queue.name = highest.name
                    queue.link = highest.detailUrl

                    waitFor = queue.waitFor * (60 * 60 * 24)

                    if queue.markComplete or (not queue.markComplete and highest.date + waitFor < time.time()):
                        if self.config.get('NZB', 'sendTo') == 'Sabnzbd' and highest.type == 'nzb':
                            success = self.sabNzbd.send(highest)
                        else:
                            success = self.blackHole(highest)
                    else:
                        success = False
                        log.info('Found %s but waiting for %d hours.' % (highest.name, ((highest.date + waitFor) - time.time()) / (60 * 60)))

                    # Set status
                    if success:
                        movie.status = u'snatched' if queue.markComplete else u'waiting'
                        movie.dateChanged = datetime.datetime.now()

                        queue.completed = True
                        Db.flush()

                    return True
                time.sleep(5)

        return False

    def blackHole(self, item):
        blackhole = self.config.get('NZB', 'blackhole') if item.type == 'nzb' else self.config.get('Torrents', 'blackhole')
        if not blackhole or not os.path.isdir(blackhole):
            log.error('No directory set for blackhole %s download.' % item.type)
        else:
            fullPath = os.path.join(blackhole, item.name + '.' + item.type)

            if not os.path.isfile(fullPath):
                log.info('Downloading %s to %s.' % (item.type, fullPath))
                file = urllib.urlopen(item.url).read()
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

def startYarrCron(config, debug, provider):
    cron = YarrCron()
    cron.config = config
    cron.debug = debug
    cron.provider = provider
    cron.start()

    return cron
