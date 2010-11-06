from app.config.wrapper import Wrapper
from app.core import getLogger
from app.core.controller import BasicController
from app.core.environment import Environment as env_
from app.lib.event import Event
from copy import copy
from mako.lookup import TemplateLookup
from mako.template import Template
import os
import urllib

log = getLogger(__name__)

### TEMP @todo: Integrate with classes.
def redirect(url):
    raise cherrypy.HTTPRedirect(url)
### /TEMP

class PluginController(BasicController):
    def __init__(self, plugin, views, mako_lookup):
        self.plugin = plugin
        self.makoLookup = mako_lookup
        self.views = views
        self.util = TemplateUtil(self)
        if os.path.isdir(self.plugin._getStaticDir()):
            env_.get('frontend').registerStaticDir(
                            '/' + self._getVirtual(['static']), # /virtualPathNoLeadingSlash
                            self.plugin._getStaticDir()
        )#register static
        self.const = {
            '_static' : self._getVirtual(['static'])
            # TEMP @todo: hack by Ruud
            , '_url': Url(self.plugin)
            , '_baseUrl': env_._baseUrl
            , '_core': '_plugins/core-34e50abc-bbdd-477c-b1e2-bb28c7fcdb7d'
            , '_plugin': self.plugin
            , '_util': self.util
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
            self.plugin._info.name + '-' + str(self.plugin._uuid),
            ] + subdirectories
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
        self._about = About(self._getAbout())
        self._configFiles = dict()
        self._configPath = os.path.join('plugins', name)
        self._env = env_
        self._info = None
        self._pluginMgr = pluginMgr
        self._pluginPath = path
        self._uuid = self._identify()
        self.name = name
        self.postConstruct()
        if self._pluginPath:
            self.makoLookup = TemplateLookup(directories = [
                os.path.join(self._pluginPath, 'views'),
                # TEMP @todo: hack by Ruud
                os.path.join(os.path.dirname(self._pluginPath), 'core', 'views')
                # /TEMP
            ])

    def postConstruct(self):
        """Stub that is invoked after constructor."""
        pass
    def init(self):
        """Stub that is invoked once all plugins have been loaded."""
        pass

    def _identify(self):
        raise RuntimeError("Plugin must provide UUID")

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

    def _getStaticDir(self, subdirectories = ()):
        return os.path.join(
            self._pluginPath,
            'static',
            *subdirectories
        )

    def _generateUrl(self):
        return '_plugins/' + self.name + '-' + str(self._uuid) + '/'

class About(object):
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

class TemplateUtil(object):
    def __init__(self, controller):
        self._controller = controller

    def eventString(self, *args, **kwargs):
        event = self._controller.plugin._fire(*args, **kwargs)
        result = event.getResultSet()
        if result:
            return str(result[0])
        return ""

    def wrap(self, prefix, suffix, contains):
        if contains:
            return prefix + contains + suffix
        return ""

class Url(object):
    def __init__(self, plugin):
        self._plugin = plugin
        self._baseUrl = plugin._generateUrl()

    def __call__(self, *args, **kwargs):
        result = self._baseUrl
        result += '/'.join(args) + '/' if args else ""
        params = urllib.urlencode(kwargs)
        result += '?' + params if params else ""

    def __str__(self):
        return self()
