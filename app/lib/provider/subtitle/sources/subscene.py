from app.config.cplog import CPLog
from app.lib.provider.subtitle.base import subtitleBase
from imdb.parser.http.bsouplxml._bsoup import BeautifulSoup
from urllib2 import URLError
from zipfile import ZipFile
import cherrypy
import hashlib
import os.path
import time
import urllib
import urllib2

log = CPLog(__name__)

class subscene(subtitleBase):

    name = 'SubScene.com'

    config = None
    extensions = []

    siteUrl = 'http://subscene.com'
    searchUrl = 'http://subscene.com/s.aspx'
    downloadUrl = 'http://subscene.com/language/movie/subtitle-%d.aspx'

    def __init__(self, config, extensions):
        self.config = config
        self.extensions = extensions

    def conf(self, value):
        return self.config.get('Subtitles', value)

    def find(self, movie):

        if not self.isAvailable(self.siteUrl):
            return

        # Only use subscene if we have original name
        if not movie.get('history'): return {}
        releaseName = movie.get('history')[0].old.split(os.path.sep)[-2]
        if not releaseName: return {}

        # Do search
        arguments = urllib.urlencode({
            'q': self.toSearchString(releaseName)
        })
        url = "%s?%s" % (self.searchUrl, arguments)

        try:
            data = self.urlopen(url, timeout = self.timeout).read()
        except (IOError, URLError):
            log.error('Failed to open %s.' % url)
            return False

        results = self.getItems(data)

        valid = []
        for lang in self.conf('languages').split(','):
            for result in results:
                if self.simplifyString(releaseName) in self.simplifyString(result['name']) and result['language'] == lang and not self.alreadyDownloaded(movie['movie'], releaseName, result['id']):
                    valid.append(result)
                    break

        sorted(valid, self.sort)

        if len(valid) > 0:
            result = valid.pop(0)
            result['forFile'] = releaseName
            return {
                'subtitles': [result],
                'language': result['language'],
                'download': self.download
            }

        return {}

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

    def getItems(self, data):

        results = []

        soup = BeautifulSoup(data)
        table = soup.find("table", { "class" : "filmSubtitleList" })

        try:
            for tr in table.findAll("tr"):
                item = {}

                for td in tr.findAll('td'):
                    if td.a:
                        spans = td.a.findAll('span')
                        if len(spans) == 2:
                            item['id'] = int(spans[1].get('id').replace('r', ''))
                            item['name'] = str(spans[1].contents[0]).strip()
                            item['rating'] = int(spans[0].get('class', '0').replace('r', ''))

                            # Language
                            lang = str(spans[0].contents[0]).strip()
                            item['language'] = self.languages.get(lang, lang)
                    if td.div:
                        item['hi'] = td.div.get('id') == 'imgEar'

                if item.get('name'):
                    results.append(item)
        except AttributeError:
            log.error('No search results.')

        return results

    def download(self, subtitle):

        subtitle = subtitle['subtitles'].pop()
        url = self.downloadUrl % subtitle['id']

        try:
            data = self.urlopen(url, timeout = self.timeout).read()
        except (IOError, URLError):
            log.error('Failed to open %s.' % url)
            return False

        soup = BeautifulSoup(data)

        postUrl = self.siteUrl + soup.find("a", {'id' : 's_lc_bcr_downloadLink' }).get('href').split('"')[-2]
        typeId = soup.find("input", {"name" : "typeId" }).get('value')
        params = urllib.urlencode({
           '__EVENTTARGET': 's$lc$bcr$downloadLink',
           '__EVENTARGUMENT': '',
           '__VIEWSTATE': soup.find("input", {"id" : "__VIEWSTATE" }).get('value'),
           '__PREVIOUSPAGE': soup.find("input", { "id" : "__PREVIOUSPAGE" }).get('value'),
           'subtitleId': soup.find("input", {"id" : "subtitleId" }).get('value'),
           'typeId': typeId,
           'filmId': soup.find("input", {"name" : "filmId" }).get('value')
        })

        # No unrarring yet
        if 'rar' in typeId:
            log.error('Unrar not supported yet.')
            return False

        req = urllib2.Request(postUrl, headers = {
            'Referer' : url,
            'User-Agent' : 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8'
        })

        subtitleFiles = []
        try:
            self.wait()
            data = urllib2.urlopen(req, params)
            self.lastUse = time.time()
            hash = hashlib.md5(url).hexdigest()

            tempdir = cherrypy.config.get('cachePath')
            tempSubtitleFile = os.path.join(tempdir, hash + '.' + typeId)

            # Remove the old
            if os.path.isfile(tempSubtitleFile): os.remove(tempSubtitleFile)

            with open(tempSubtitleFile, 'wb') as f:
                f.write(data.read())

            if 'zip' in typeId:
                zip = ZipFile(tempSubtitleFile)

                extract = []
                for name in zip.namelist():
                    for ext in self.extensions:
                        if ext.replace('*', '') in name:
                            subtitleFiles.append(os.path.join(tempdir, name))
                            extract.append(name)

                zip.extractall(tempdir, extract)
                os.remove(tempSubtitleFile)
            else:
                subtitleFiles.append(tempSubtitleFile)

            log.info('Subtitle download "%s" finished. %dKB.' % (subtitle['name'], int(data.info().getheaders("Content-Length")[0]) / 1024))
            return subtitleFiles

        except:
            log.error('Subtitle download %s failed.' % subtitle['name'])
            return False

    languages = {
        "None"                : "none",
        "Albanian"            : "sq",
        "Arabic"              : "ar",
        "Belarusian"          : "hy",
        "Bosnian"             : "bs",
        "BosnianLatin"        : "bs",
        "Bulgarian"           : "bg",
        "Catalan"             : "ca",
        "Chinese"             : "zh",
        "Croatian"            : "hr",
        "Czech"               : "cs",
        "Danish"              : "da",
        "Dutch"               : "nl",
        "English"             : "en",
        "Esperanto"           : "eo",
        "Estonian"            : "et",
        "Farsi"               : "fa",
        "Persian"             : "fa",
        "Finnish"             : "fi",
        "French"              : "fr",
        "Galician"            : "gl",
        "Georgian"            : "ka",
        "German"              : "de",
        "Greek"               : "el",
        "Hebrew"              : "he",
        "Hindi"               : "hi",
        "Hungarian"           : "hu",
        "Icelandic"           : "is",
        "Indonesian"          : "id",
        "Italian"             : "it",
        "Japanese"            : "ja",
        "Kazakh"              : "kk",
        "Korean"              : "ko",
        "Latvian"             : "lv",
        "Lithuanian"          : "lt",
        "Luxembourgish"       : "lb",
        "Macedonian"          : "mk",
        "Malay"               : "ms",
        "Norwegian"           : "no",
        "Occitan"             : "oc",
        "Polish"              : "pl",
        "Portuguese"          : "pt",
        "PortugueseBrazil"    : "pb",
        "Portuguese (Brazil)" : "pb",
        "Brazilian"           : "pb",
        "Romanian"            : "ro",
        "Russian"             : "ru",
        "SerbianLatin"        : "sr",
        "Serbian"             : "sr",
        "Slovak"              : "sk",
        "Slovenian"           : "sl",
        "Spanish"             : "es",
        "Swedish"             : "sv",
        "Syriac"              : "syr",
        "Thai"                : "th",
        "Turkish"             : "tr",
        "Ukrainian"           : "uk",
        "Urdu"                : "ur",
        "Vietnamese"          : "vi",
        "English (US)"        : "en",
        "All"                 : "all"
    }
