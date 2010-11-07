from app.core import env_

def load(plugin):
    owner = env_._pluginMgr.getMyPlugin(__name__)
    class Base(owner._import.frontend.widget):
        def __init__(self):
            self._owner = plugin
            super(Base, self).__init__('Base', plugin)

    Base()
