from app.config.cplog import CPLog
from app.lib.provider.subtitle.base import subtitleBase
from urllib2 import URLError
import base64
import cherrypy
import os
import struct
import time
import xmlrpclib
import zlib

log = CPLog(__name__)

class openSubtitles(subtitleBase):

    name = "OpenSubtitles"
    siteUrl = "http://www.opensubtitles.org/"
    searchUrl = "http://api.opensubtitles.org/xml-rpc"

    def __init__(self, config, extensions):
        self.config = config
        self.extensions = extensions

        #Login
        self.wait()
        self.server = xmlrpclib.Server(self.searchUrl)
        self.lastUse = time.time()

        try:
            log_result = self.server.LogIn("", "", "eng", "CouchPotato")
            self.token = log_result["token"]
        except Exception:
            log.error("Open subtitles could not be contacted for login")
            self.token = None

    def conf(self, value):
        return self.config.get('Subtitles', value)

    def find(self, movie):

        if not self.isAvailable(self.siteUrl):
            return

        data = {
            'subtitles': [],
            'language': '',
            'download': self.download
        }

        self.wait()

        for lang in self.conf('languages').split(','):
            for file in movie['files']:
                filePath = os.path.join(movie['path'], file['filename'])
                search = {
                    'moviehash': self.hashFile(filePath),
                    'moviebytesize': str(os.path.getsize(filePath)),
                    'sublanguageid': self.languages.get(lang)
                }

                results = self.getItems(movie, file, search)
                sorted(results, self.sort)

                if len(results) > 0:
                    result = results.pop(0)
                    data['language'] = result['language']
                    data['subtitles'].append(result)

            if len(data['subtitles']) == len(movie['files']):
                return data

        self.lastUse = time.time()

        return data

    def getItems(self, movie, file, params):

        subtitles = []
        results = []

        try:
            if params:
                results = self.server.SearchSubtitles(self.token, [params])
        except Exception, e:
            log.error("Couldn\'t search OpenSubtitles: %s, token:%s, params:%s, result:%s" % (e, self.token, params, results))
            return subtitles

        if results.get('data'):
            for r in results['data']:
                if int(r['SubBad']) == 0:
                    item = {}
                    item['id'] = r['IDSubtitleFile']
                    item['name'] = r['SubFileName']
                    item['rating'] = r['SubDownloadsCnt']
                    item['link'] = r['SubDownloadLink']
                    item['hi'] = r['SubHearingImpaired']
                    item['language'] = r['ISO639']
                    item['forFile'] = file['filename']

                    if not self.alreadyDownloaded(movie['movie'], item['forFile'], item['id']):
                        subtitles.append(item)

        return subtitles

    def download(self, data):

        ids = []
        names = {}
        for subtitle in data['subtitles']:
            ids.append(subtitle['id'])
            names[subtitle['id']] = subtitle['name']

        try:
            self.wait()
            data = self.server.DownloadSubtitles(self.token, ids)
            self.lastUse = time.time()
            log.info('Subtitle download "%s" finished.' % subtitle['name'])
        except (IOError, URLError):
            log.error('Failed to open %s.' % data['subtitles'])
            return None

        subtitlesFiles = []
        tempdir = cherrypy.config.get('cachePath')
        for base in data['data']:
            data = base['data']
            data = base64.b64decode(data)
            data = zlib.decompress(data, 15 + 32)

            tempSubtitleFile = os.path.join(tempdir, names[base['idsubtitlefile']])

            # Remove the old
            if os.path.isfile(tempSubtitleFile): os.remove(tempSubtitleFile)

            dump = open(tempSubtitleFile, "wb")
            dump.write(data)
            dump.close()

            subtitlesFiles.append(tempSubtitleFile)

        return subtitlesFiles

    def sort(self, a, b):
        if a.get('rating') > b.get('rating'):
            if a.get('hi') and not b.get('hi'):
                return 1
            if not a.get('hi') and b.get('hi'):
                return - 1

        if a.get('rating') < b.get('rating'):
            if b.get('hi') and not a.get('hi'):
                return 1
            if not b.get('hi') and a.get('hi'):
                return - 1

        return 0

    def hashFile(self, name):
        try:
            longlongformat = 'q'  # long long 
            bytesize = struct.calcsize(longlongformat)

            f = open(name, "rb")

            filesize = os.path.getsize(name)
            hash = filesize

            if filesize < 65536 * 2:
                return "SizeError"

            for x in range(65536 / bytesize):
                buffer = f.read(bytesize)
                (l_value,) = struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  


            f.seek(max(0, filesize - 65536), 0)
            for x in range(65536 / bytesize):
                buffer = f.read(bytesize)
                (l_value,) = struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF

            f.close()
            returnedhash = "%016x" % hash
            return returnedhash

        except(IOError):
            return False

    languages = {
        "en": "eng",
        "fr" : "fre",
        "hu": "hun",
        "cs": "cze",
        "pl" : "pol",
        "sk" : "slo",
        "pt" : "por",
        "pt-br" : "pob",
        "es" : "spa",
        "el" : "ell",
        "ar":"ara",
        'sq':'alb',
        "hy":"arm",
        "ay":"ass",
        "bs":"bos",
        "bg":"bul",
        "ca":"cat",
        "zh":"chi",
        "hr":"hrv",
        "da":"dan",
        "nl":"dut",
        "eo":"epo",
        "et":"est",
        "fi":"fin",
        "gl":"glg",
        "ka":"geo",
        "de":"ger",
        "he":"heb",
        "hi":"hin",
        "is":"ice",
        "id":"ind",
        "it":"ita",
        "ja":"jpn",
        "kk":"kaz",
        "ko":"kor",
        "lv":"lav",
        "lt":"lit",
        "lb":"ltz",
        "mk":"mac",
        "ms":"may",
        "no":"nor",
        "oc":"oci",
        "fa":"per",
        "ro":"rum",
        "ru":"rus",
        "sr":"scc",
        "sl":"slv",
        "sv":"swe",
        "th":"tha",
        "tr":"tur",
        "uk":"ukr",
        "vi":"vie"
    }
