from minify.js import jsmin
from minify.css import cssmin
import cherrypy
import logging
import os

log = logging.getLogger(__name__)

class Minify():
    
    comment = {
       'style': '/*** %s:%d ***/\n',
       'script': '// %s:%d\n'
    }

    def css(self, files = [], out = '_Minified.css'):
        return self.minify('style', files, out)

    def js(self, files = [], out = '_Minified.js'):
        return self.minify('script', files, out)
    
    def minify(self, type, files, out):
        base = os.path.join(cherrypy.config.get('basePath'), 'media', type)
        url = 'cache/minify/' + out
        cache = os.path.join(cherrypy.config.get('runPath'), 'cache', 'minify')
        out = os.path.join(cache, out)
        
        # Check for dates, minify only on newer files
        goMinify = True
        if os.path.isfile(out):
            outTimestamp = int(os.path.getmtime(out))
            goMinify = False
            for file in files:
                fullPath = os.path.join(base, file)
                if int(os.path.getmtime(fullPath)) > outTimestamp:
                    goMinify = True

        if goMinify:
            log.debug('Minifying JS.')
        
            # Create dir
            self.makeDirs(cache)

            raw = []
            for file in files:
                fullPath = os.path.join(base, file)
                f = open(fullPath, 'r').read()
                
                if type == 'script':
                    data = jsmin(f)
                else:
                    data = cssmin(f)
                
                raw.append({'file': file, 'date': int(os.path.getmtime(fullPath)), 'data': data})
            
            # Combine all files together with some comments
            data = ''
            for r in raw:
                data += self.comment.get(type) % (r.get('file'), r.get('date'))
                data += r.get('data') + '\n\n'

            data.strip()
            self.write(data, out)

        outTimestamp = int(os.path.getmtime(out))
        return url+'?'+str(outTimestamp)
    
    def makeDirs(self, dir):
        try:
            os.makedirs(dir)
        except OSError:
            pass

    def write(self, data, file):
        log.debug('Writing %s' % file)
        with open(file, 'w') as f:
            f.write(data)
