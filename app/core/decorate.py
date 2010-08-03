from app.core.environment import Environment
def listen(to, config = None):
    def listen_(func):
        def wrapper(*args, **kwargs):
            Environment.get('pluginMgr').listen(to, func, config)
            return func(*args, **kwargs)
        return wrapper
    return listen_
