'''
This class initializes the cherrypy subsystem.
'''
import cherrypy

cherrypy.config.update({
    'global': {
        'server.thread_pool':               10,
        'server.socket_port':           int(ca.get('global', 'port')),
        'server.socket_host':               ca.get('global', 'host'),
        'server.Environment':               ca.get('global', 'server.Environment'),
        'engine.autoreload_on':             ca.get('global', 'engine.autoreload_on') and not options.daemonize,
        'tools.mako.collection_size':       500,
        'tools.mako.directories':           os.path.join(path_base, 'app', 'views'),

        'basePath':                         path_base,
        'runPath':                          rundir,
        'cachePath':                        ca.get('paths', 'cache'),
        'frozen':                           frozen,

        # Global workers
        'config':                           ca,
        'updater':                          myUpdater,
        'cron':                             myCrons.threads,
        'searchers':                        myCrons.searchers,
        'flash':                            app.flash()
    }
})

# Static config
conf = {
    '/': {
        'request.dispatch': Routes(),
        'tools.sessions.on':  True,
        'tools.sessions.timeout': 240,

        'tools.gzip.on': True,
        'tools.gzip.mime_types': ['text/html', 'text/plain', 'text/css', 'text/javascript', 'application/javascript']
    },
    '/media':{
        'tools.staticdir.on': True,
        'tools.staticdir.root': path_base,
        'tools.staticdir.dir': "media",
        'tools.expires.on': True,
        'tools.expires.secs': 3600 * 24 * 7
    },
    '/cache':{
        'tools.staticdir.on': True,
        'tools.staticdir.root': rundir,
        'tools.staticdir.dir': "cache",
        'tools.expires.on': True,
        'tools.expires.secs': 3600 * 24 * 7
    }
}

# Don't use auth when password is empty
if ca.get('global', 'password') != '':
    conf['/'].update({
        'tools.basic_auth.on': True,
        'tools.basic_auth.realm': 'Awesomeness',
        'tools.basic_auth.users': {ca.get('global', 'username'):ca.get('global', 'password')},
        'tools.basic_auth.encrypt': app.clearAuthText
    })
    cherrypy.tools.mybasic_auth = cherrypy.Tool('on_start_resource', app.basicAuth)

# I'll do my own logging, thanks!
cherrypy.log.error_log.propagate = False
cherrypy.log.access_log.propagate = False

#No Root controller as we provided all our own.
cherrypy.tree.mount(root = None, config = conf)
