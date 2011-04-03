# Based on netprowl by the following authors.

# Altered 1st October 2010 - Tim Child.
# Have added the ability for the command line arguments to take a password.

# Altered 1-17-2010 - Tanner Stokes - www.tannr.com
# Added support for command line arguments

# ORIGINAL CREDITS
# """Growl 0.6 Network Protocol Client for Python"""
# __version__ = "0.6.3"
# __author__ = "Rui Carmo (http://the.taoofmac.com)"
# __copyright__ = "(C) 2004 Rui Carmo. Code under BSD License."
# __contributors__ = "Ingmar J Stein (Growl Team), John Morrissey (hashlib patch)"

from app.config.cplog import CPLog
import base64
import cherrypy
import urllib
import urllib2

try:
  import hashlib
  md5_constructor = hashlib.md5
except ImportError:
  import md5
  md5_constructor = md5.new

import struct

from socket import AF_INET, SOCK_DGRAM, socket

GROWL_UDP_PORT=9887
GROWL_PROTOCOL_VERSION=1
GROWL_TYPE_REGISTRATION=0
GROWL_TYPE_NOTIFICATION=1

log = CPLog(__name__)

class GROWL:

    hosts = []
    password = ''

    def __init__(self):
        self.enabled = self.conf('enabled');
        self.hosts = [x.strip() for x in self.conf('host').split(",")]
        self.password = self.conf('password')
        pass

    def conf(self, options):
        return cherrypy.config['config'].get('GROWL', options)

    def notify(self, message, title):
        if not self.enabled:
            return

        # default priority
        priority = 0
        # default stickiness
        sticky = False

        for curHost in self.hosts:
            # connect up to Growl server machine
            addr = (curHost, GROWL_UDP_PORT)

            s = socket(AF_INET,SOCK_DGRAM)
            # register application with remote Growl
            p = GrowlRegistrationPacket(password=self.password)
            p.addNotification()
            # send registration packet
            s.sendto(p.payload(), addr)

            # assemble notification packet
            p = GrowlNotificationPacket(title=title, description=message, priority=priority, sticky=sticky,password=self.password)

            # send notification packet
            s.sendto(p.payload(), addr)
            s.close()

    def updateLibrary(self):
        #For uniformity reasons not removed
        return

    def test(self, hosts, password):

        self.enabled = True
        self.hosts = [x.strip() for x in hosts.split(",")]
        self.password = password

        self.notify('ZOMG Lazors Pewpewpew!', 'Test Message')

#end class

class GrowlRegistrationPacket:
  """Builds a Growl Network Registration packet.
     Defaults to emulating the command-line growlnotify utility."""

  def __init__(self, application="NetGrowl", password = None ):
    self.notifications = []
    self.defaults = [] # array of indexes into notifications
    self.application = application.encode("utf-8")
    self.password = password
  # end def

  def addNotification(self, notification="Command-Line Growl Notification", enabled=True):
    """Adds a notification type and sets whether it is enabled on the GUI"""
    self.notifications.append(notification)
    if enabled:
      self.defaults.append(len(self.notifications)-1)
  # end def

  def payload(self):
    """Returns the packet payload."""
    self.data = struct.pack( "!BBH",
                             GROWL_PROTOCOL_VERSION,
                             GROWL_TYPE_REGISTRATION,
                             len(self.application) )
    self.data += struct.pack( "BB",
                              len(self.notifications),
                              len(self.defaults) )
    self.data += self.application
    for notification in self.notifications:
      encoded = notification.encode("utf-8")
      self.data += struct.pack("!H", len(encoded))
      self.data += encoded
    for default in self.defaults:
      self.data += struct.pack("B", default)
    self.checksum = md5_constructor()
    self.checksum.update(self.data)
    if self.password:
       self.checksum.update(self.password)
    self.data += self.checksum.digest()
    return self.data
  # end def
# end class

class GrowlNotificationPacket:
  """Builds a Growl Network Notification packet.
     Defaults to emulating the command-line growlnotify utility."""

  def __init__(self, application="NetGrowl",
               notification="Command-Line Growl Notification", title="Title",
               description="Description", priority = 0, sticky = False, password = None ):

    self.application  = application.encode("utf-8")
    self.notification = notification.encode("utf-8")
    self.title        = title.encode("utf-8")
    self.description  = description.encode("utf-8")
    flags = (priority & 0x07) * 2
    if priority < 0:
      flags |= 0x08
    if sticky:
      flags = flags | 0x0100
    self.data = struct.pack( "!BBHHHHH",
                             GROWL_PROTOCOL_VERSION,
                             GROWL_TYPE_NOTIFICATION,
                             flags,
                             len(self.notification),
                             len(self.title),
                             len(self.description),
                             len(self.application) )
    self.data += self.notification
    self.data += self.title
    self.data += self.description
    self.data += self.application
    self.checksum = md5_constructor()
    self.checksum.update(self.data)
    if password:
       self.checksum.update(password)
    self.data += self.checksum.digest()
  # end def

  def payload(self):
    """Returns the packet payload."""
    return self.data
  # end def
# end class