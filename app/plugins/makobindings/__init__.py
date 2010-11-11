from . import makobindings
def start(*args, **kwargs):
    return makobindings.Mako(*args, **kwargs)
