def init_logging(target, debug = False):
    app.configLogging(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'debug.conf' if debug else 'logging.conf'), target)
    return logging.getLogger(__name__)
