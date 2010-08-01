'''
Created on 31.07.2010

@author: Christian
'''

from app.environment import Environment as _env

p = OptionParser()
p.add_option('-d', action = "store_true",
             dest = 'daemonize', help = "Run the server as a daemon")
p.add_option('-q', '--quiet', action = "store_true",
             dest = 'quiet', help = "Don't log to console")
p.add_option('-p', '--pidfile',
             dest = 'pidfile', default = None,
             help = "Store the process id in the given file")
p.add_option('-t', '--debug', action = "store_true",
             dest = 'debug', help = "Run in debug mode")

options, args = p.parse_args()

config = 'data/config.ini'
if args.__len__() == 1:
    config = args[0]
elif args.__len__() > 1:
    print ('Invalid argument cound: [config path]')
    sys.exit(1)

_env.setBasePath(os.path.dirname(config))
config_name = os.path.basename(config)
#Load Configuration
try:
    ca = Global(config_name)
    _env.cfg = ca;

except Exception as e:
    print 'Could not initialize config. Check the path' + str(e)
    sys.exit(1)



# Stop logging
if options.quiet:
    cherrypy.config.update({'log.screen': False})
    pass

# Deamonize
if options.daemonize:
    cherrypy.config.update({'log.screen': False})
    plugins.Daemonizer(cherrypy.engine).subscribe()

# PIDfile
if options.pidfile:
    plugins.PIDFile(cherrypy.engine, options.pidfile).subscribe()
