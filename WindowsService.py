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

import win32service
import win32event


class MyService(win32serviceutil.ServiceFramework):
    """NT Service."""

    service_name = 'MovieManager'
    service_display_name = 'MovieManager'
    service_description = 'Automatic NZB Movie Downloading.'
    iniFile = 'config.ini'

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
        s.run(['--log-file', 'logs/MovieManager.log', self.iniFile])
        
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        #win32event.SetEvent(self.stop_event)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        sys.exit()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MyService)
