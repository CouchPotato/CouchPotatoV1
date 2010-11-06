from app.core import getLogger

class Event(object):
    def __init__(self, sender, name, *args, **kwargs):
        self._sender = sender
        self._name = name
        self._args = args
        self._kwargs = kwargs
        self._resultSets = [[]]

    def addResult(self, result):
        """Append results to the Event"""
        if not self._resultSets:
            self._resultSets = [[]]

        self._resultSets[0].append(result)

    def addResults(self, results):
        '''add elements of an iterable at the end of the results list'''
        for result in results:
            self.addResult(result)

    def addResultSet(self, result_set):
        self._resultSets.insert(0, result_set)

    def getResultSet(self, position = 0):
        """
        Return the most recent result set.
        Use the additional parameter position to
        access an older set of results.
        """
        return self._resultSets[position]

    def getResultSets(self):
        """Return the result sets"""
        return self._resultSets

    def setResults(self, results):
        """
        override the current set of results.
        """
        self._resultSets[0] = results

    def clear(self):
        self._resultSets = [[]]


def extract(func):
    """Extract event parameters and pass as parameters."""
    def extractor(self, event, config, *args, **kwargs):
        if kwargs:
            getLogger(__name__).warn("kwargs present while extracting parameters.")

        kwargs.update({'_event' : event, '_config' : config})
        kwargs.update(event._kwargs)
        return func(self, *(event._args + args), **kwargs)
    return extractor
