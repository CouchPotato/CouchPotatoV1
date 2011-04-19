# -*- coding: utf-8 -*-
# Copyright (c) 2008-2010 Erik Svensson <erik.public@gmail.com>
# Licensed under the MIT license.

class TransmissionError(Exception):
    """
	This exception is raised when there has occured an error related to
	communication with Transmission. It is a subclass of Exception.
    """
    def __init__(self, message='', original=None):
        Exception.__init__(self)
        self.message = message
        self.original = original

    def __str__(self):
        return self.message

class HTTPHandlerError(Exception):
    """
	This exception is raised when there has occured an error related to
	the HTTP handler. It is a subclass of Exception.
    """
    def __init__(self, httpurl=None, httpcode=None, httpmsg=None, httpheaders=None, httpdata=None):
        Exception.__init__(self)
        self.url = ''
        self.code = 600
        self.message = ''
        self.headers = {}
        self.data = ''
        if isinstance(httpurl, (str, unicode)):
            self.url = httpurl
        if isinstance(httpcode, (int, long)):
            self.code = httpcode
        if isinstance(httpmsg, (str, unicode)):
            self.message = httpmsg
        if isinstance(httpheaders, (dict)):
            self.headers = httpheaders
        if isinstance(httpdata, (str, unicode)):
            self.data = httpdata

    def __repr__(self):
        return '<HTTPHandlerError %d, %s>' % (self.code, self.message)

    def __str__(self):
        return '<HTTPHandlerError %d, %s>' % (self.code, self.message)

    def __unicode__(self):
        return u'<HTTPHandlerError %d, %s>' % (self.code, self.message)
