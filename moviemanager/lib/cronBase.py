import threading

class cronBase(threading.Thread):

    abort = False
    running = False

    def isRunning(self):
        return self.running

    def quit(self):
        self.abort = True

    def canShutdown(self):
        return (self.abort and not self.running)
