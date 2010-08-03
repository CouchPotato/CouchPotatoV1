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
frontend = core.frontend.bootstrap()
frontend.registerStaticDir('/_cache', 'cache', env_.get('dataDir'))
core.extend()
frontend.start()
