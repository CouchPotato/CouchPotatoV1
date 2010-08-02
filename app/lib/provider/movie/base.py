from app.lib.provider.rss import rss
from app.lib.providers.providerInfo import ProviderInfo
from app.config.section import Section

class MovieBase(rss):
    providerInfo = ProviderInfo()
    type = 'movie'

    def __init__(self, config):
        self._className = self.__class__.__name__
        self.config = Section(self._className, config)
        self.initConfigSettings()
        self.initProviderInfo()
        pass


    def initConfigSettings(self):
        raise NotImplemented()

    def initProviderInfo(self):
        c = self.config
        pi = self.providerInfo
        pi.author = c.get('author')
        pi.name = c.get('name')
        pi.support = c.get('support')
        pi.url = c.get('url')
        pi.version = c.get('version')
