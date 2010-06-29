from app.lib.cron.cronNzb import startNzbCron
from app.lib.cron.cronRenamer import startRenamerCron
from app.lib.cron.cronTrailer import startTrailerCron, trailerQueue
from app.lib.provider.movie.search import movieSearcher
from app.lib.provider.nzb.search import nzbSearcher
from app.lib.sabNzbd import sabNzbd
from cherrypy.process import plugins
import cherrypy
import logging

log = logging.getLogger(__name__)

class CronJobs(plugins.SimplePlugin):
    """A feature that does something."""

    config = {}
    threads = {}
    searchers = {}

    def __init__(self, bus, config):
        plugins.SimplePlugin.__init__(self, bus)

        log.info("Starting Cronjobs.")
        self.config = config

        #searchers
        nzbSearch = nzbSearcher(config);
        movieSearch = movieSearcher(config);
        self.searchers['nzb'] = nzbSearch
        self.searchers['movie'] = movieSearch

        #nzb cronjob
        nzbCronJob = startNzbCron(config)
        nzbCronJob.provider = nzbSearch
        nzbCronJob.sabNzbd = sabNzbd(config)
        self.threads['nzb'] = nzbCronJob
        
        #trailer cron
        trailerCronJob = startTrailerCron(config)
        self.threads['trailer'] = trailerCronJob
        self.searchers['trailerQueue'] = trailerQueue
        
        #renamer cron
        renamerCronJob = startRenamerCron(config, self.searchers)
        self.threads['renamer'] = renamerCronJob

    def start(self):
        return True

    def stop(self):
        log.info("Stopping Cronjobs.")
        for t in self.threads.itervalues():
            if t.quit:
                t.quit()
            t.join()


##searchers
#nzbSearch = nzbSearcher(ca);
#movieSearch = movieSearcher(ca);
#config['pylons.app_globals'].searcher['nzb'] = nzbSearch
#config['pylons.app_globals'].searcher['movie'] = movieSearch
#
##trailer cron
#trailerCronJob = startTrailerCron(ca)
#config['pylons.app_globals'].cron['trailer'] = trailerCronJob
#config['pylons.app_globals'].cron['trailerQueue'] = trailerQueue
#
##nzb search cron
#nzbCronJob = startNzbCron(ca)
#nzbCronJob.provider = nzbSearch
#nzbCronJob.sabNzbd = sabNzbd(ca)
#config['pylons.app_globals'].cron['nzb'] = nzbCronJob
#
##renamer cron
#renamerCronJob = startRenamerCron(ca, config['pylons.app_globals'].searcher, trailerQueue)
#config['pylons.app_globals'].cron['renamer'] = renamerCronJob
