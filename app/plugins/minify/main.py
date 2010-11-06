from app.plugins.minify.css import cssmin
from app.plugins.minify.js import jsmin
import logging
import os
from app.lib.bones import PluginBones
import uuid
from app.lib import event

log = logging.getLogger(__name__)

class Minify(PluginBones):
    """Provide header and scriptstyle by wrapping Minify"""

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

    def _identify(self):
        return uuid.UUID('95f1d3b9-0c27-423a-b1ed-fe25c2c4798b')

    def init(self):
        self._listen('registerStyle', self.registerStyle)
        self._listen('registerScript', self.registerScript)

        self._listen('getStyle', self.style)
        self._listen('getScripts', self.scripts)

    @event.extract
    def style(self, as_html = False, _event = None, location = 'head', **kwargs):
        url = self.minify('style', location)
        if as_html:
            url = '<link href="%s" rel="stylesheet" type="text/css" />' % url
        _event.addResult(url)

    @event.extract
    def scripts(self, as_html = False, _event = None, location = 'head', **kwargs):
        url = self.minify('script', location)
        _event.addResult(url)

    @event.extract
    def registerStyle(self, file, _event, position = 'head', **kwargs):
        baseUrl = _event._sender._getStaticDir()
        self.register(os.path.join(baseUrl, 'style', file), 'style', position)

    @event.extract
    def registerScript(self, file, _event, position = 'body', **kwargs):
        baseUrl = _event._sender._getStaticDir()
        self.register(os.path.join(baseUrl, 'style', file), 'script', position)

    def register(self, file, type, location):

        if not self.files[type].get(location):
            self.files[type][location] = []

        filePath = file
        self.files[type][location].append(filePath)

    def minify(self, type, location):
        log.info("Minifying")
        if type not in self.files:
            raise RuntimeError("Inexistent type: %s" % type)

        files = self.files[type][location] if location in self.files[type] else []
        extension = 'js' if type == 'script' else 'css'
        cache = self._getCachePath()
        out = os.path.join(cache, location + "." + extension)

        # Check for dates, minify only on newer files
        doMinify = True
        if os.path.isfile(out):
            outTimestamp = int(os.path.getmtime(out))
            doMinify = False
            for file in files:
                if int(os.path.getmtime(file)) > outTimestamp:
                    doMinify = True

        if doMinify:
            log.debug('Minifying JS.')

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
        return self._url(
            'cache'
            , '%s.%s' % (location, extension)
            , timestamp = str(outTimestamp)
        )

    def write(self, data, file):
        log.debug('Writing %s' % file)
        with open(file, 'w') as f:
            f.write(data)

    def _getCachePath(self):
        return self._getCacheDir()
