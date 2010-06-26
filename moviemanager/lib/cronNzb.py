from moviemanager.lib.cronBase import cronBase
from moviemanager.model import Movie, History
from moviemanager.model.meta import Session as Db
import datetime
import logging
import time

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
        time.sleep(10)

        while True and not self.abort:

            #check single movie
            for movie in self.checkTheseMovies:
                self._searchNzb(movie)
                self.checkTheseMovies.pop(0)
                #log.info('Sleeping search for 5 sec')
                time.sleep(5)

            #check all movies
            now = time.time()
            if (self.lastChecked + self.intervalSec) < now:
                self.lastChecked = now
                self.searchNzbs()

            #log.info('Sleeping NzbCron for %d seconds' % 10)
            time.sleep(60)

        log.info('NzbCron has shutdown.')
        
    def setInterval(self, interval):
        self.intervalSec = int(interval) * 60 * 60

    def forceCheck(self, movie = None):
        if movie == None:
            self.lastChecked = time.time() - self.intervalSec + 10
        else:
            self.checkTheseMovies.append(movie)

    def searchNzbs(self):
        log.info('Searching for NZB.')
        self.doCheck()

        #get al wanted movies
        movies = Db.query(Movie).filter_by(status = u'want')

        for movie in movies:
            self._searchNzb(movie)

            #log.info('Sleeping search for 5 sec')
            time.sleep(5)

        self.doCheck(False)
        log.info('Finished search.')


    def _searchNzb(self, movie):

        results = self.provider.find(movie)

        #search for highest score
        highest = None
        highestScore = 0
        for result in results:
            if result.score > highestScore:
                highest = result

        #send highest to SABnzbd & mark as snatched
        if highest:
            success = self.sabNzbd.send(highest)

            # Add name to history for renaming
            if success:
                movie.status = u'snatched'

                newHistory = History()
                newHistory.movieId = movie.id
                newHistory.name = highest.name
                Db.add(newHistory)
                Db.commit()


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

def startNzbCron(config):
    cron = NzbCron()
    cron.config = config
    cron.start()

    return cron
