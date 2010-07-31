if __name__ == '__main__':
    import sys
    import os

    from app import core




    # Include paths
    #sys.path.insert(0, path_base)
    #sys.path.insert(0, os.path.join(path_base, 'library'))

    #log = logging.getLogger(__name__)

    #initDb()
    #core._env.cfg.get('global', 'server_config')
    #core._env.loadConfig()
    web_boot = core.frontend.Bootstraper('default')
    web_boot.registerStaticDir('/media', 'media')






