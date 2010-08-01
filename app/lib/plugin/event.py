class Event(object):
    def __init__(self, sender, name, input):
        self.sender = sender
        self.name = name
        self.input = input
        self.results = [[]]

    def addResult(self, result):
        self.results[0].append(result)

    def getResults(self):
        return self.results[0]

    def setResults(self, results):
        self.results.insert(0, results)


