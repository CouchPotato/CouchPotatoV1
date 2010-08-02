class Event(object):
    def __init__(self, sender, name, input):
        self.sender = sender
        self.senderName = sender.name
        self.name = name
        self.input = input
        self.results = [[]]

    def addResult(self, result):
        self.results[0].append(result)

    def getResult(self, position = 0):
        return self.results[position]

    def setResults(self, results):
        self.results.insert(0, results)


