if __name__ == '__main__':
    import sys
    import os

    from app import core
    from app.core.environment import Environment as env_




    # Include paths
    #sys.path.insert(0, path_base)
    #sys.path.insert(0, os.path.join(path_base, 'library'))

    #log = logging.getLogger(__name__)

    #initDb()
    #core._env.cfg.get('global', 'server_config')
    #core._env.loadConfig()
    core.bootstrap()
    web_boot = core.frontend.Bootstraper()
    web_boot.registerStaticDirAbs(
        '/', '', env_.get('appDir')
    )
    web_boot.registerStaticDir('/media', 'media')
    web_boot.registerStaticDirAbs(
        '/cache', 'cache', env_.get('dataDir')
    )

