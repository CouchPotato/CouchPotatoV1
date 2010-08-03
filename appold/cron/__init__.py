from app.lib.cron.cronETA import startEtaCron, etaQueue
from app.lib.cron.cronRenamer import startRenamerCron
from app.lib.cron.cronTrailer import startTrailerCron, trailerQueue
from app.lib.cron.cronYarr import startYarrCron
from app.lib.provider.movie.search import movieSearcher
from app.lib.provider.yarr.search import Searcher
from app.lib.sabNzbd import sabNzbd
from cherrypy.process import plugins
import cherrypy
import logging
import sys
import traceback

log = logging.getLogger(__name__)

# Log error to file
class LogFile(object):
    """File-like object to log text using the `logging` module."""

    def __init__(self, name = None):
        self.logger = logging.getLogger(name)

    def write(self, msg, level = logging.INFO):
        if 'Traceback' in msg and not 'bsouplxml' in msg:
            self.logger.critical(msg)

    def flush(self):
        pass

class CronJobs(plugins.SimplePlugin):

    config = {}
    threads = {}
    searchers = {}

    def __init__(self, bus, config):
        plugins.SimplePlugin.__init__(self, bus)

        self.config = config

    def start(self):

        config = self.config

        log.info("Starting Cronjobs.")
        self.config = config

        #searchers
        try:
            yarrSearch = Searcher(config);
            movieSearch = movieSearcher(config);
            self.searchers['yarr'] = yarrSearch
            self.searchers['movie'] = movieSearch
        except Exception as e:
            log.info('Could not initialize searchers: ' + str(e) + ''+traceback.format_exc())
            raise RuntimeError('Failed to initialize searchers.')

        #trailer cron
        trailerCronJob = startTrailerCron(config)
        self.threads['trailer'] = trailerCronJob
        self.searchers['trailerQueue'] = trailerQueue

        etaCron = startEtaCron()
        self.threads['eta'] = etaCron
        self.searchers['etaQueue'] = etaQueue

        #renamer cron
        renamerCronJob = startRenamerCron(config, self.searchers)
        self.threads['renamer'] = renamerCronJob

        #nzb cronjob
        yarrCronJob = startYarrCron(config, yarrSearch)
        yarrCronJob.sabNzbd = sabNzbd(config)
        self.threads['yarr'] = yarrCronJob

        #log all errors/tracebacks to logfile
        sys.stderr = LogFile('stderr')

    def stop(self):
        log.info("Stopping Cronjobs.")
        for t in self.threads.itervalues():
            if t.quit:
                t.quit()
            t.join()

    start.priority = 70
