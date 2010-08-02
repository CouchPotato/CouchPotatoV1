from app.lib.plugin.bones import Bones
import cherrypy
class Frontend(Bones):
    '''
    Provides an interterface for plugins to register with the frontend
    '''


    def postConstruct(self):
        self.tabs = {}

    def export(self):
        return {
            'frontend' : (
                          'discoverTabs'
                          )
                }

    def addTab(self, name, title, controller):
        pass

    def addSmallTab(self, name, title, controller):
        pass


