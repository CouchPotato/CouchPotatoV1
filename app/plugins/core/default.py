from app.lib.bones import PluginBones, PluginController
from app.lib.event import Event
import cherrypy
from app.core.frontend import Route
from app.core.environment import Environment as env_
from app.plugins.core.threaded import EventThread
from app.core import getLogger

class CoreController(PluginController):
    @cherrypy.expose
    def index(self):
        vars = {'baseUrl' : env_.get('baseUrl')}
        return self.render('index.html', vars)


class CouchCore(PluginBones):
    '''
    classdocs
    '''

    def postConstruct(self):
        pass
        self._listen('threaded.event.wait', self.threadedEvent, True)
        self._listen('threaded.event', self.threadedEvent, False)

    def init(self):
        controller = self._createController((), CoreController)
        route = Route(controller = controller, route = '/')
        self._fire('threaded.event.wait', 'frontend.route.register', route)

    def threadedEvent(self, event, wait):
        """
        Call all listeners to a given event name
        simultaneously by spawning a thread for each listener.
        
        Pass arguments for the event to simulate
        as you would with _fire, just set them as additional parameters
        
        Make the events' workers timeout by specifying a keyworded
        parameter _timeout
        
        Force a custom class by specifying the type using _eventClass
        
        Results:
            wait:
                only one result set available. The most
                recent resultSet's elemtns from an Event are added
                to this event's results.
                
            no wait:
                one result set, two Results: the first
                contains a list with all the events,
                the second a list with all threads.
        
        """

        positional = event._args
        keyworded = event._kwargs
        event_class = keyworded.get('_eventClass', Event)
        timeout = keyworded.get('_timeout', None)

        trash = event_class(event._sender, *positional, **keyworded)
        callbacks, configs = self._pluginMgr.getListeners(trash._name)

        threads = []
        events = []
        for callback, config in zip(callbacks.itervalues(), configs.itervalues()):
            new_event = event_class(event._sender, *positional, **keyworded)
            thread = EventThread(new_event, callback, config)
            events.append(new_event)
            threads.append(thread)
            thread.start()
        log = getLogger(__name__)
        if wait:
            for i, thread in enumerate(threads):
                if thread.isAlive():
                    log.info('Waiting for worker ' + str(i))
                thread.join(timeout)
                if thread.isAlive(): log.info('Timeout hit on worker ' + str(i))
                else: event.addResults(events[i].getResultSet())
            #for end
            return
        #endif wait
        event.addResult(events)
        event.addResult(threads)
        return

def threadedEventWrapper(self, *args, **kwargs):
    return self._fire('threaded.event', *args, **kwargs)
def threadedEventWaitWrapper(self, *args, **kwargs):
    return self._fire('threaded.event.wait', *args, **kwargs)


PluginBones._threaded = threadedEventWrapper
PluginBones._threadedWait = threadedEventWaitWrapper


