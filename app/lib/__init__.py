
def cleanHost(host):
    if not host.startswith(('http://', 'https://')):
        host = 'http://' + host

    if not host.endswith('/'):
        host += '/'

    return host
