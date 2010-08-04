class Event(object):
    def __init__(self, sender, name, input, *args, **kwargs):
        self._sender = sender
        self._name = name
        self._input = input
        self._results = [[]]

    def addResult(self, result):
        self._results[0].append(result)

    def getResult(self, position = 0):
        return self._results[position]

    def setResults(self, results):
        self.results._insert(0, results)


