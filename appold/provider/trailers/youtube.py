from app.lib.provider.rss import rss
from urllib2 import URLError
import logging
import re
import urllib
import urllib2
import xml.etree.ElementTree as XMLTree

log = logging.getLogger(__name__)

class Youtube(rss):

    apiUrl = 'http://gdata.youtube.com/feeds/api/videos'
    watchUrl = 'http://www.youtube.com/watch?v='
    getVideoUrl = 'http://www.youtube.com/get_video?video_id=%s&t=%s&fmt=%d'

    formats = {
        '1080p':{'format': 'mp4', 'quality': 'High Quality (1080p)', 'key': 37},
        '720p': {'format': 'mp4', 'quality': 'High Quality (720p)', 'key': 22},
        '480p': {'format': 'mp4', 'quality': 'High Quality (480p)', 'key': 18}
    }

    def __init__(self, config):
        self.config = config

    def conf(self, value):
        return self.config.get('Trailer', value)

    def find(self, movie):
        arguments = urllib.urlencode({
            'category':'trailer',
            'orderby':'relevance',
            'alt':'rss',
            'q': self.toSaveString(movie.name + ' ' + str(movie.year)),
            'max-results': 5
        })
        url = "%s?%s" % (self.apiUrl, arguments)

        log.info('Searching: %s', url)

        data = urllib.urlopen(url)

        if data:
            log.debug('Parsing YouTube RSS.')
            try:

                try:
                    xml = self.getItems(data)
                except:
                    log.error('No valid xml, to many requests? Try again in 15sec.')
                    return

                videos = []
                for video in xml:
                    id = self.gettextelement(video, "guid").split('/').pop()
                    key = self.findKey(id)
                    videos.append({'id':id, 'key':key})

                return self.findQuality(videos)

            except SyntaxError:
                log.debug('Failed')
                return False

    def findKey(self, videoId):
        url = self.videoUrl(videoId)
        data = urllib.urlopen(url).read()
        try:
            m = re.search('&t=(?P<id>.*?)&', data)
            return m.group('id')
        except AttributeError:
            return None

    def findQuality(self, videos):

        results = {'480p':[], '720p':[], '1080p':[]}
        for video in videos:
            for quality, format in self.formats.iteritems():
                videoUrl = self.getVideoUrl % (video['id'], video['key'], int(format['key']))

                try:
                    videoData = urllib2.urlopen(videoUrl, timeout = self.timeout)
                    if videoData:
                        meta = videoData.info()
                        size = int(meta.getheaders("Content-Length")[0])
                        if size > 0:
                            results[quality].append(videoUrl)
                except (IOError, URLError):
                    pass

        return results

    def getItems(self, data):
        return XMLTree.parse(data).findall('channel/item')

    def videoUrl(self, id):
        return self.watchUrl + id
