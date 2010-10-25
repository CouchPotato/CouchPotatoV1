# Author: Nic Wolfe <nic@wolfeden.ca>
# URL: http://code.google.com/p/sickbeard/
#
# This file is part of Sick Beard.
#
# Sick Beard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard. If not, see <http://www.gnu.org/licenses/>.


import urllib, urllib2
import socket
import sys
import base64
import time, struct

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

def sendToXBMC(command, host, username, password):
    '''
Handles communication with XBMC servers

command - Dictionary of field/data pairs, encoded via urllib.urlencode and
passed to /xbmcCmds/xbmcHttp

host - host/ip + port (foo:8080)
'''

    for key in command:
        if type(command[key]) == unicode:
            command[key] = command[key].encode('utf-8')

    enc_command = urllib.urlencode(command)

    # Web server doesn't like POST, GET is the way to go
    url = 'http://%s/xbmcCmds/xbmcHttp/?%s' % (host, enc_command)
    print url

    try:
        # If we have a password, use authentication
        req = urllib2.Request(url)
        if password:
            base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
            authheader = "Basic %s" % base64string
            req.add_header("Authorization", authheader)

        handle = urllib2.urlopen(req)
        response = handle.read()
    except IOError, e:
        # print "Warning: Couldn't contact XBMC HTTP server at " + host + ": " + str(e)
        response = ''

    return response

def notifyXBMC(header, message, host, username, password):
    for curHost in [x.strip() for x in host.split(",")]:
        command = {'command': 'ExecBuiltIn', 'parameter': 'Notification(%s, %s)' % (header, message)}
        request = sendToXBMC(command, curHost, username, password)

def updateLibrary(host, username, password):
    updateCommand = {'command': 'ExecBuiltIn', 'parameter': 'XBMC.updatelibrary(video)'}
    request = sendToXBMC(updateCommand, host, username, password)

    if not request:
        return False

    return True

# Wake function
def wakeOnLan(ethernet_address):
    addr_byte = ethernet_address.split(':')
    hw_addr = struct.pack('BBBBBB', int(addr_byte[0], 16),
    int(addr_byte[1], 16),
    int(addr_byte[2], 16),
    int(addr_byte[3], 16),
    int(addr_byte[4], 16),
    int(addr_byte[5], 16))

    # Build the Wake-On-LAN "Magic Packet"...
    msg = '\xff' * 6 + hw_addr * 16

    # ...and send it to the broadcast address using UDP
    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ss.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ss.sendto(msg, ('<broadcast>', 9))
    ss.close()

# Test Connection function
def isHostUp(host,port):

    (family, socktype, proto, garbage, address) = socket.getaddrinfo(host, port)[0]
    s = socket.socket(family, socktype, proto)

    try:
        s.connect(address)
        return "Up"
    except:
        return "Down"


def checkHost(host, port):

    # we should try to get this programmatically from the IP
    mac = ""

    i=1
    while isHostUp(host,port)=="Down" and i<4:
        wakeOnLan(mac)
        time.sleep(20)
        i=i+1