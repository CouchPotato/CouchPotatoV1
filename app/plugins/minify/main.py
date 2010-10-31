from app.core import env_
from app.plugins.minify.css import cssmin
from app.plugins.minify.js import jsmin
import cherrypy
import logging
import os

log = logging.getLogger(__name__)

class Minify():
    '''
    This plugin provides the header script & style
    '''

    comment = {
       'style': '/*** %s:%d ***/\n',
       'script': '// %s:%d\n'
    }

    files = {
        'style': {
        },
        'script': {
        }
    }

    def init(self):

        self._listen('registerStyle', self.registerStyle)
        self._listen('registerScript', self.registerScript)

        self._listen('getStyle', self.style)
        self._listen('getScripts', self.scripts)

    def style(self, location = 'head'):
        return self.minify('style', location)

    def scripts(self, location = 'head'):
        return self.minify('script', location)

    def registerStyle(self, file, position = 'head'):
        self.register(file, 'style', position)

    def registerScript(self, file, position = 'body'):
        self.register(file, 'script', position)

    def register(self, file, type, location):

        if not self.files[type].get(location):
            self.files[type].insert(location, [])
        
        filePath = 'plugins/xxx/' + file
        self.files[type][location].append(filePath)

    def minify(self, type, files, location):
        extention = 'js' if type == 'js' else 'css'
        url = 'cache/minify/%s.%s' % (location, extention)
        cache = os.path.join(env_._appDir, 'cache', 'minify')
        out = os.path.join(cache, location)

        # Check for dates, minify only on newer files
        goMinify = True
        if os.path.isfile(out):
            outTimestamp = int(os.path.getmtime(out))
            goMinify = False
            for file in files:
                if int(os.path.getmtime(file)) > outTimestamp:
                    goMinify = True

        if goMinify:
            log.debug('Minifying JS.')

            # Create dir
            self.makeDirs(cache)

            raw = []
            for file in files:
                f = open(file, 'r').read()
                data = jsmin(f) if type == 'script' else cssmin(f)
                raw.append({'file': file, 'date': int(os.path.getmtime(file)), 'data': data})

            # Combine all files together with some comments
            data = ''
            for r in raw:
                data += self.comment.get(type) % (r.get('file'), r.get('date'))
                data += r.get('data') + '\n\n'

            data.strip()
            self.write(data, out)

        outTimestamp = int(os.path.getmtime(out))
        return url + '?' + str(outTimestamp)

    def makeDirs(self, dir):
        try:
            os.makedirs(dir)
        except OSError:
            pass

    def write(self, data, file):
        log.debug('Writing %s' % file)
        with open(file, 'w') as f:
            f.write(data)
