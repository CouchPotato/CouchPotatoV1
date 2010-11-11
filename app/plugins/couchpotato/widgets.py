from app.core import env_

def load(plugin):
    owner = env_._pluginMgr.getMyPlugin(__name__) #@UndefinedVariable
    class Base(owner._import.frontend.widget):
        def render(self):
            pass

    class Tab(owner._import.frontend.widget):
        pass

    Base('base', owner)
    Tab('tab', owner)
