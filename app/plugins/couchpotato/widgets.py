from app.core import env_

def load(plugin):
    owner = env_._pluginMgr.getMyPlugin(__name__) #@UndefinedVariable
    class Base(owner._import.frontend.widget):
        def _execute(self, context, args, kwargs, config_args, config_kwargs):
            return owner._mako.render("base.html", {'mycontext' : context})

    class Tab(owner._import.frontend.widget):
        def _execute(self, context, args, kwargs, config_args, config_kwargs):
            name, url = args
            vars = { 'mycontext' : context, 'myname' : name, 'myurl' : url}
            return owner._mako.render("tab.html", vars)

    Base('base', owner)
    Tab('tab', owner)
