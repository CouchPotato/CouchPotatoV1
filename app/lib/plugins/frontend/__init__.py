from app.lib.plugins.frontend.frontend import Frontend
def start(name, pluginMgr):
    return Frontend(name, pluginMgr)
