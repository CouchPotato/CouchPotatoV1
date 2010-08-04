class Event(object):
    def __init__(self, sender, name, input, *args, **kwargs):
        self._sender = sender
        self._name = name
        self._input = input
        self._results = [[]]

    def addResult(self, result):
        '''append results to the Event'''
        self._results[0].append(result)

    def addResults(self, self, results):
        '''add elements of an iterable at the end of the results list'''
        for result in results:
            self.addResult(result)

    def getResult(self, position = 0):
        """
        Return the most recent result set.
        Use the additional parameter position to
        access an older set of results.
        """
        return self._results[position]

    def setResults(self, results):
        """
        introduce a new set of results.
        this can be useful for filtering results
        while retaining the previous state.
        """
        self.results._insert(0, results)


