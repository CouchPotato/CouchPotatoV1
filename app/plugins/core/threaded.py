import threading
from app.lib.event import Event
from app.core import getLogger
import time

class EventThread(threading.Thread):
    """
    classdocs
    """

    def __init__(self, event, callback, config):
        """
        Create a new, suspended Thread that, when run,
        will simulate an event firing by calling the
        provided callback with its associated class
        and an event constructed from the type event_class.
        
        Pass the arguments that are received in positional and
        keyworded to the event by python * and ** means.
        """
        threading.Thread.__init__(self)
        self._event = event
        self._callback = callback
        self._config = config

    def run(self):
        log = getLogger(__name__)
        getLogger(__name__).info('SIMULATING: ' + self._event._name)
        self._callback(self._event, self._config)
        log.info('Worker terminated.')
        pass
