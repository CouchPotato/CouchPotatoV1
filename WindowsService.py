"""
url: http://wiki.pylonshq.com/display/pylonscookbook/How+to+run+Pylons+as+a+Windows+service7
The most basic (working) Windows service possible.
Requires Mark Hammond's pywin32 package.  
Most of the code was taken from a  CherryPy 2.2 example of how to set up a service
"""
import pkg_resources
import win32serviceutil
from paste.script.serve import ServeCommand as Server
import os, sys
import ConfigParser

import win32service
import win32event

class DefaultSettings(object):
    def __init__(self):
        if os.path.dirname(__file__):
            os.chdir(os.path.dirname(__file__))
        # find the ini file
        self.ini = [x for x in os.listdir('.')
            if os.path.splitext(x)[1].lower().endswith('ini')]
        # create a config parser opject and populate it with the ini file
        c = ConfigParser.SafeConfigParser()
        c.read(self.ini[0])
        self.c = c

    def getDefaults(self):
        '''
        Check for and get the default settings
        '''
        if (
            (not self.c.has_section('winservice')) or
            (not self.c.has_option('winservice', 'service_name')) or
            (not self.c.has_option('winservice', 'service_display_name')) or
            (not self.c.has_option('winservice', 'service_description'))
            ):
            print 'setting defaults'
            self.setDefaults()
        service_name = self.c.get('winservice', 'service_name')
        service_display_name = self.c.get('winservice', 'service_display_name')
        service_description = self.c.get('winservice', 'service_description')
        iniFile = self.ini[0]
        return service_name, service_display_name, service_description, iniFile

    def setDefaults(self):
        '''
        set and add the default setting to the ini file
        '''
        if not self.c.has_section('winservice'):
            self.c.add_section('winservice')
        self.c.set('winservice', 'service_name', 'WSCGIService')
        self.c.set('winservice', 'service_display_name', 'WSCGI windows service')
        self.c.set('winservice', 'service_description', 'WSCGI windows service')
        cfg = file(self.ini[0], 'wb')
        self.c.write(cfg)
        cfg.close()
        print '''
you must set the winservice section service_name, service_display_name,
and service_description options to define the service 
in the %s file
''' % self.ini[0]
        sys.exit()


class MyService(win32serviceutil.ServiceFramework):
    """NT Service."""

    d = DefaultSettings()
    service_name, service_display_name, service_description, iniFile = d.getDefaults()

    _svc_name_ = service_name
    _svc_display_name_ = service_display_name
    _svc_description_ = service_description

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        # create an event that SvcDoRun can wait on and SvcStop
        # can set.
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def SvcDoRun(self):
        os.chdir(os.path.dirname(__file__))
        s = Server(None)
        s.run([self.iniFile])
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        #win32event.SetEvent(self.stop_event)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        sys.exit()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MyService)
