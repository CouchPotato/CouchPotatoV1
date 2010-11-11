from app.lib.bones import PluginBones
from app.core import env_
import uuid
from copy import copy
import os
from mako.lookup import TemplateLookup
from mako.template import Template

class Mako(PluginBones):
    def postConstruct(self):
        self.installMakoNamespace()

    def _identify(self):
        return uuid.UUID('3ea20b9e-41d0-4199-b9d6-8acc0bc8a0c1')

    def _getDependencies(self):
        return {}

    def getConstants(self, plugin):
        return {
            '_static' : plugin._getVirtual(['static'])
            # TEMP @todo: hack by Ruud
            , '_url': plugin._url
            , '_baseUrl': env_._baseUrl
            , '_core': '_plugins/core-34e50abc-bbdd-477c-b1e2-bb28c7fcdb7d'
            , '_plugin': plugin
            , '_util': TemplateUtil(plugin)
            # /TEMP
        }

    def getViewPath(self, plugin):
        views_path = [plugin._pluginPath, 'views']
        #views_path.extend(view_subfolders)
        return os.path.join(*views_path)

    def getLookup(self, plugin):
        return TemplateLookup(directories = [
            os.path.join(plugin._pluginPath, 'views'),
            # TEMP @todo: hack by Ruud
            os.path.join(os.path.dirname(plugin._pluginPath), 'core', 'views')
            # /TEMP
        ])

    def render(self, plugin, name, vars = None, *args):
        vars = copy(vars) if vars else {}
        const = self.getConstants(plugin)
        vars.update(const)
        views = self.getViewPath(plugin)
        name = os.path.join(views, name)
        template = Template(filename = name, lookup = self.getLookup(plugin))
        return template.render_unicode(*args, **vars)

    def installMakoNamespace(self):
        mako_self = self
        class MakoNamespace(object):
            def __init__(self):
                self._owner = None
                def renderWrapper(*args, **kwargs):
                    return mako_self.render(self._owner, *args, **kwargs)
                self.render = renderWrapper

            def __get__(self, owner, type):
                self._owner = owner
                return self

            def __getattr__(self, name):
                if name == "render":
                    return self.render
                raise AttributeError("No other methods accessible.")

        PluginBones._mako = MakoNamespace()


class TemplateUtil(object):
    def __init__(self, plugin):
        self._plugin = plugin

    def eventString(self, *args, **kwargs):
        event = self._plugin._fire(*args, **kwargs)
        result = event.getResultSet()
        if result:
            return str(result[0])
        return ""

    def wrap(self, prefix, suffix, contains):
        if contains:
            return prefix + contains + suffix
        return ""


