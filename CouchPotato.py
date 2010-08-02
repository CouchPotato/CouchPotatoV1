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
#core.bootstrap()
core.bootstrap()
web_boot = core.frontend.bootstrap()
web_boot.registerStaticDir(
    '/', '', env_.get('appDir')
)
web_boot.registerStaticDir('/media', env_.get('appDir'), 'media')
web_boot.registerStaticDir(
    '/cache', env_.get('dataDir'), 'cache'
)
core.extend()
frontend = core.frontend.Frontend()
frontend.start()
