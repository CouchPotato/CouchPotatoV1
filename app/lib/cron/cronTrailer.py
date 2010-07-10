from app.lib.cron.cronBase import cronBase
from app.lib.provider.rss import rss
import Queue
import logging
import os
import re
import shutil
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
            try:
                movie = trailerQueue.get(timeout = 1)

                #do a search
                self.running = True
                self.search(movie['movie'], movie['destination'])
                self.running = False

                trailerQueue.task_done()
            except Queue.Empty:
                pass


        log.info('TrailerCron shutting down.')

    def search(self, movie, destination):

        for video in self.getVideos(movie, destination):
            key = self.findKey(video.id)
            downloaded = self.download(movie, video.id, key, destination)
            if downloaded:
                break

    def getVideos(self, movie, destination):
        arguments = urllib.urlencode({
            'category':'trailer',
            'orderby':'relevance',
            'alt':'rss',
            'q': self.toSaveString(movie.name + ' ' + str(movie.year)),
            'max-results': 5
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

        for format in self.formats:
            log.debug('Format %d >= %d' % (format['key'], int(self.config.get('Renamer', 'trailerQuality'))))
            videoUrl = self.getVideoUrl % (videoId, key, int(format['key']))
            videoData = urllib.urlopen(videoUrl)
            if videoData:
                meta = videoData.info()
                size = int(meta.getheaders("Content-Length")[0])
                if size > 0:

                    #trails destination
                    trailerFile = os.path.join(destination, 'movie-trailer' + '.' + format['format'])
                    tempTrailerFile = os.path.join(destination, '_DOWNLOADING-trailer' + '.' + format['format'])
                    if os.path.isfile(tempTrailerFile): os.remove(tempTrailerFile)
                    if not os.path.isfile(trailerFile):
                        log.info('Downloading trailer in %s too "%s", size: %s' % (format['quality'], destination, str(size / 1024 / 1024) + 'MB'))
                        with open(tempTrailerFile, 'w') as f:
                            f.write(videoData.read())

                        #temp to real
                        log.info('Download finished, renaming trailer temp-download to final.')
                        os.rename(tempTrailerFile, trailerFile)

                        # Use same permissions as parent dir
                        try:
                            #mode = os.stat(destination)
                            #os.chmod(trailerFile, mode[ST_MODE] & 07777)
                            shutil.copymode(destination, trailerFile)
                        except OSError:
                            log.error('Failed setting permissions for %s' % trailerFile)

                        return True

            if format['key'] == int(self.config.get('Renamer', 'trailerQuality')):
                log.debug('Minumum trailer quality exceeded.')
                return False

        return False

    def getItems(self, data):
        return XMLTree.parse(data).findall('channel/item')

    def videoUrl(self, id):
        return self.watchUrl + id

def startTrailerCron(config):
    cron = TrailerCron()
    cron.config = config
    cron.start()

    return cron
