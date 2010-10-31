from app.config.wrapper import Wrapper
from app.core import env_, getLogger
from app.core.controller import BasicController
from app.lib.event import Event
from copy import copy
from mako.lookup import TemplateLookup
from mako.template import Template
import cherrypy
import os
import traceback
import urllib

log = getLogger(__name__)

### TEMP
def url(*args, **kwargs):
    url = kwargs.get('controller') + '/' + kwargs.get('action') + '/'
    for key in ['controller', 'action']:
        if kwargs.get(key):
            del kwargs[key]

    params = urllib.urlencode(kwargs)

    return url + '?'+params if params else ''

def redirect(url):
    raise cherrypy.HTTPRedirect(url)
### /TEMP

class PluginController(BasicController):
    def __init__(self, plugin, views, mako_lookup):
        self.plugin = plugin
        self.makoLookup = mako_lookup
        self.views = views
        if os.path.isdir(self._getStaticDir()):
            env_.get('frontend').registerStaticDir(
                            '/' + self._getVirtual(['static']), # /virtualPathNoLeadingSlash
                            self._getStaticDir()
        )#register static
        self.const = {
            '_static' : self._getVirtual(['static'])
            # TEMP
            , '_url': url
            , '_baseUrl': env_._baseUrl
            , '_core': '_plugins/core-1/static'
            , '_plugin': self.plugin
            # /TEMP
        }

    def render(self, name, vars = None, *args):
        vars = copy(vars) if vars else {}
        vars.update(self.const)
        name = os.path.join(self.views, name)
        template = Template(filename = name, lookup = self.makoLookup)
        return template.render_unicode(*args, **vars)

    def _getVirtual(self, subdirectories = None):
        subdirectories = subdirectories or []
        return '/'.join([
            '_plugins',
            self.plugin._info.name + '-' + str(self.plugin._info.version),
            ] + subdirectories
        )

    def _getStaticDir(self, subdirectories = ()):
        return os.path.join(
            self.plugin._pluginPath,
            'static',
            *subdirectories
        )

    def _getPlugin(self, name):
        return env_.get('_pluginMgr').getPlugin(name)

class PluginBones(object):
    '''
    This class handles the loading of plugin-defined configuration files.
    '''

    def __init__(self, name, pluginMgr, path = None, *args, **kwargs):
        '''
        Constructor
        '''
        self.name = name
        self._info = None
        self._pluginPath = path
        self._pluginMgr = pluginMgr
        self._configPath = os.path.join('plugins', name)
        self._configFiles = dict()
        self._about = About(self._getAbout())
        self.postConstruct()
        if self._pluginPath:
            self.makoLookup = TemplateLookup(directories = [
                os.path.join(self._pluginPath, 'views'),
                # TEMP
                os.path.join(os.path.dirname(self._pluginPath), 'core', 'views')
                # /TEMP
            ])

    def postConstruct(self):
        '''stub that is invoked after constructor'''
        pass
    def init(self):
        pass

    def _loadConfig(self, name):
        cf = self._configFiles
        if cf.has_key(name):
            return cf[name]

        filename = os.path.join(self._configPath, name)
        try:
            cf[name] = Wrapper(filename)
        except:
            log.info('Failed to load config: ' + str(filename) + "\n" + traceback.format_exc())
            pass

    def _loadConfigSet(self, nameSet):
        for name in nameSet:
            self._loadConfig(name)

    def _getConfig(self, name, builder = None):
        if self._configFiles.has_key(name):
            return self._configFiles[name]
        raise Exception('Config inexistent.')

    def _getPluginMgr(self):
        return env_.get('pluginManager')

    def _getAbout(self):
        return {}

    def _fire(self, name, *args, **kwargs):
        return self._fireCustom(Event, name, *args, **kwargs)

    def _getDbSession(self):
        return env_.get('db').createSession()

    def _fireCustom(self, EventType, *args, **kwargs):
        event = EventType(self, *args, **kwargs)
        return self._pluginMgr.fire(event)

    def _listen(self, to, callback, config = None, position = -1):
        self._pluginMgr.listen(to, callback, config, position)

    def _createController(self, view_subfolders = (), ControllerType = PluginController):
        #DEFAULT: I assume that () as default is acceptable because () is an immutable object
        views_path = [self._pluginPath, 'views']
        views_path.extend(view_subfolders)
        views_path = os.path.join(*views_path)
        return ControllerType(self, views_path, self.makoLookup)

    def _upgradeDatabase(self, latest_version, scope):
        '''Call this to automatically upgrade your tables'''
        env_.get('db').upgradeDatabase(self._info, latest_version, scope)


class About:
    def __init__(self, info_dict):
        self.name = None
        self.author = None
        self.description = None
        self.version = None
        self.email = None
        self.logo = None
        self.www = None
        self.fromDict(info_dict)

    def fromDict(self, dict):
        attrs = (
            'name', 'author',
            'description', 'version',
            'email', 'logo', 'www'
        )
        for attr in attrs:
            if dict.has_key(attr):
                setattr(self, attr, dict[attr])
