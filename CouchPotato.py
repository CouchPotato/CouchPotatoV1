import sys
import os

import chapbucket

# Make sure 'plugins' is considered a module
open('plugins/__init__.py', 'w').close()
chapbucket.bootstrap()
# frontend = core.frontend.bootstrap()
# frontend.registerStaticDir('/_cache', 'cache', env_.get('dataDir'))
chapbucket.extend({
    'user' : ('plugins.', sys.path[0]),
    'couchpotato' : ('couchpotato.plugins.',
                     os.path.join(__file__, 'couchpotato', 'plugins')
                     ),
})
