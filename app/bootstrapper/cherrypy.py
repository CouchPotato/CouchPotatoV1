'''
Created on 31.07.2010

@author: Christian
'''


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