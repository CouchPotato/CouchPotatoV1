from app.config.cplog import CPLog
import cherrypy
import urllib
import urllib2
import telnetlib
import re

log = CPLog(__name__)

class NMJ:

    host = ''
    database = ''
    mount = ''

    def __init__(self):
        self.enabled = self.conf('enabled');
        self.host = self.conf('host')
        self.database = self.conf('database')
        self.mount = self.conf('mount')
        pass

    def conf(self, options):
        return cherrypy.config['config'].get('NMJ', options)

    def auto(self, host):
        terminal = False
        try:
            terminal = telnetlib.Telnet(host)
        except Exception:
            log.error(u"Warning: unable to get a telnet session to %s" % (host))
            return False

        log.debug(u"Connected to %s via telnet" % (host))
        terminal.read_until("sh-3.00# ")
        terminal.write("cat /tmp/source\n")
        terminal.write("cat /tmp/netshare\n")
        terminal.write("exit\n")
        tnoutput = terminal.read_all()

        match = re.search(r"(.+\.db)\r\n?(.+)(?=sh-3.00# cat /tmp/netshare)", tnoutput)

        if match:
            database = match.group(1)
            device = match.group(2)
            log.info(u"Found NMJ database %s on device %s" % (database, device))
            self.database = database
        else:
            log.error(u"Could not get current NMJ database on %s, NMJ is probably not running!" % (host))
            return False

        if device.startswith("NETWORK_SHARE/"):
            match = re.search(".*(?=\r\n?%s)" % (re.escape(device[14:])), tnoutput)

            if match:
                mount = match.group().replace("127.0.0.1", host)
                log.info(u"Found mounting url on the Popcorn Hour in configuration: %s" % (mount))
                self.mount = mount
            else:
                log.error("Detected a network share on the Popcorn Hour, but could not get the mounting url")
                return False

        return '{"database": "%(database)s", "mount": "%(mount)s"}' % {"database": database, "mount": mount}

    def notify(self, message):
        #For uniformity reasons not removed
        return

    def updateLibrary(self):
        if not self.enabled:
            return False

        if self.mount:
            try:
                req = urllib2.Request(self.mount)
                log.debug(u"Try to mount network drive via url: %s" % (self.mount))
                handle = urllib2.urlopen(req)
            except IOError, e:
                log.error(u"Warning: Couldn't contact popcorn hour on host %s: %s" % (self.host, e))
                return False

        params = {
            "arg0": "scanner_start",
            "arg1": self.database,
            "arg2": "background",
            "arg3": ""}
        params = urllib.urlencode(params)
        UPDATE_URL = "http://%(host)s:8008/metadata_database?%(params)s"
        updateUrl = UPDATE_URL % {"host": self.host, "params": params}

        try:
            req = urllib2.Request(updateUrl)
            log.debug(u"Sending NMJ scan update command via url: %s" % (updateUrl))
            handle = urllib2.urlopen(req)
            response = handle.read()
        except IOError, e:
            log.error(u"Warning: Couldn't contact Popcorn Hour on host %s: %s" % (host, e))
            return False

        try:
            et = etree.fromstring(response)
            result = et.findtext("returnValue")
        except SyntaxError, e:
            log.error(u"Unable to parse XML returned from the Popcorn Hour: %s" % (e))
            return False

        if int(result) > 0:
            log.error(u"Popcorn Hour returned an errorcode: %i" % (result))
            return False
        else:
            log.info("NMJ started background scan")
            return True


    def test(self, host, database, mount):

        self.enabled = True
        self.host = host
        self.database = database
        self.mount = mount

        self.updateLibrary()
