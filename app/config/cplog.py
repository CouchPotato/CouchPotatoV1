from cherrypy import _cperror
from logging import handlers
import cherrypy
import datetime
import logging
import os

class CPLog():

    context = ''

    def __init__(self, context = ''):
        self.context = context
        self.logger = cherrypy.log

    def info(self, msg):
        self.log(msg, severity = logging.INFO)

    def debug(self, msg):
        self.log(msg, severity = logging.DEBUG)

    def error(self, msg):
        self.log(msg, severity = logging.ERROR)

    def log(self, msg = '', severity = logging.INFO):
        self.logger.error(msg = msg, context = self.context, severity = severity)

    def config(self, logPath, debug = False):

        level = logging.DEBUG if debug else logging.INFO

        # Overwrite functions
        self.logger.time = self.time
        self.logger.error = self.logError
        self.logger.access = self.access

        # Set screen and level
        self.logger.screen = debug
        self.logger.error_log.setLevel(level)

        # Create log dir
        if not os.path.isdir(logPath):
            os.mkdir(logPath)

        self.logger.error_file = ""

        # Create RotatingFileHandler
        h = handlers.RotatingFileHandler(os.path.join(logPath, 'CouchPotato.log'), 'a', 500000, 4)
        h.setLevel(level)
        h.setFormatter(logging.Formatter('%(asctime)s %(levelname)-5.5s %(message)s', '%H:%M:%S'))
        self.logger.error_log.addHandler(h)

    def access(self):
        pass

    def logError(self, msg = '', context = '', severity = logging.INFO, traceback = False):

        if traceback:
            msg += _cperror.format_exc()

        context = context if context else self.context
        self.logger.error_log.log(severity, '[%+25.25s] %s' % (context[-25:], msg))

    def time(self):
        now = datetime.datetime.now()
        return ('[%02d:%02d:%02d]' % (now.hour, now.minute, now.second))
