from moviemanager.lib.cronBase import cronBase
from moviemanager.lib.provider.rss import rss
import Queue
import logging
import os
import re
import urllib
import xml.etree.ElementTree as XMLTree

trailerQueue = Queue.Queue()
log = logging.getLogger(__name__)

class TrailerCron(rss, cronBase):

    apiUrl = 'http://gdata.youtube.com/feeds/api/videos'
    watchUrl = 'http://www.youtube.com/watch?v='
    getVideoUrl = 'http://www.youtube.com/get_video?video_id=%s&t=%s&fmt=%d'

    formats = [
        {'format': 'mp4', 'quality': 'High Quality (1080p)', 'key': 37},
        {'format': 'mp4', 'quality': 'High Quality (720p)', 'key': 22},
        {'format': 'mp4', 'quality': 'High Quality (480p)', 'key': 18},
        {'format': 'flv', 'quality': 'High Quality (480p)', 'key': 35},
        {'format': 'flv', 'quality': 'High Quality (320p)', 'key': 34},
        {'format': '3gp', 'quality': 'High Quality', 'key': 36},
        {'format': '3gp', 'quality': 'Medium Quality', 'key': 17},
        {'format': '3gp', 'quality': 'Low Quality', 'key': 13},
        {'format': 'flv', 'quality': 'Low Quality', 'key': 6},
        {'format': 'flv', 'quality': 'Low Quality', 'key': 5},
    ]

    config = None

    def run(self):
        log.info('TrailerCron thread is running.')

        while True and not self.abort:
            movie = trailerQueue.get()

            #do a search
            self.running = True
            self.search(movie['movie'], movie['destination'])
            self.running = False

            trailerQueue.task_done()

        log.info('TrailerCron shutting down.')

    def search(self, movie, destination):

        for video in self.getVideos(movie, destination):
            key = self.findKey(video.id)
            self.download(movie, video.id, key, destination)

    def getVideos(self, movie, destination):
        arguments = urllib.urlencode({
            'category':'trailer',
            'orderby':'relevance',
            'alt':'rss',
            'q': self.toSaveString(movie.name + ' ' + str(movie.year)),
            'max-results': 1
        })
        url = "%s?%s" % (self.apiUrl, arguments)

        log.info('Search url: %s', url)

        data = urllib.urlopen(url)

        if data:
            log.info('Parsing YouTube RSS.')
            try:

                try:
                    xml = self.getItems(data)
                except:
                    log.error('No valid xml, to many requests? Try again in 15sec.')
                    return

                results = []
                for video in xml:

                    id = self.gettextelement(video, "guid").split('/').pop()

                    new = self.feedItem()
                    new.id = id

                    results.append(new)

                return results
            except SyntaxError:
                log.error('Failed to parse XML response from NZBs.org')
                return False

    def findKey(self, videoId):
        url = self.videoUrl(videoId)
        data = urllib.urlopen(url).read()
        m = re.search('&t=(?P<id>.*?)&', data)
        return m.group('id')

    def download(self, movie, videoId, key, destination):

        minimumExceeded = False

        for format in self.formats:
            videoUrl = self.getVideoUrl % (videoId, key, int(format['key']))
            videoData = urllib.urlopen(videoUrl)
            if videoData:
                meta = videoData.info()
                size = int(meta.getheaders("Content-Length")[0])
                if size > 0:
                    if not minimumExceeded:
                        log.info('Downloading trailer (%s) to "%s", size: %s' % (format['quality'], destination, str(size / 1024 / 1024) + 'MB'))

                        #trails destination
                        trailerFile = os.path.join(destination, 'movie-trailer' + '.' + format['format'])
                        if not os.path.isfile(trailerFile):
                            with open(trailerFile, 'w') as f:
                                f.write(videoData.read())

                        return
                    if int(self.config.get('Renamer', 'trailerQuality')) == format['key']:
                        minimumExceeded = True

    def getItems(self, data):
        return XMLTree.parse(data).findall('channel/item')

    def videoUrl(self, id):
        return self.watchUrl + id

def startTrailerCron(config):
    cron = TrailerCron()
    cron.config = config
    cron.start()

    return cron
