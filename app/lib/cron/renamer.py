from app import latinToAscii
from app.config.cplog import CPLog
from app.config.db import Movie, RenameHistory, Session as Db, MovieQueue
from app.lib.cron.base import cronBase
from app.lib.qualities import Qualities

from app.lib import xbmc
from library.xmg import xmg
import fnmatch
import os
import re
import shutil
import time
import traceback
import cherrypy

log = CPLog(__name__)

class RenamerCron(cronBase):

    ''' Cronjob for renaming movies '''

    lastChecked = 0
    interval = 1 #minutes
    intervalSec = 10
    config = {}
    trailer = {}
    minimalFileSize = 1024 * 1024 * 10 # 10MB
    ignoredInPath = ['_unpack', '_failed_', '_unknown_', '_exists_', '.appledouble', '/._'] #unpacking, smb-crap

    # Filetypes
    movieExt = ['*.mkv', '*.wmv', '*.avi', '*.mpg', '*.mpeg', '*.mp4', '*.m2ts', '*.iso', '*.img']
    nfoExt = ['*.nfo']
    audioCodecs = ['DTS', 'AC3', 'AC3D', 'MP3']
    videoCodecs = ['x264', 'DivX', 'XViD']
    subExt = ['*.sub', '*.srt', '*.idx', '*.ssa', '*.ass']
    sourceMedia = { 'bluray': ['bluray', 'blu-ray', 'brrip', 'br-rip'],
                    'hddvd': ['hddvd', 'hd-dvd'],
                    'dvd': ['dvd'],
                    'hdtv': ['hdtv']}

    def conf(self, option):
        return self.config.get('Renamer', option)

    def run(self):
        log.info('Renamer thread is running.')

        self.intervalSec = (self.interval * 60)

        if not os.path.isdir(self.conf('download')):
            log.info("Watched folder doesn't exist.")

        wait = 0.1 if self.debug else 5

        #time.sleep(10)
        while True and not self.abort:
            now = time.time()
            if (self.lastChecked + self.intervalSec) < now:
                self.running = True
                self.lastChecked = now
                self.doRename()
                self.running = False

            time.sleep(wait)

        log.info('Renamer has shutdown.')

    def isDisabled(self):
        if (self.conf('enabled') and os.path.isdir(self.conf('download')) and self.conf('download') and self.conf('destination') and self.conf('foldernaming') and self.conf('filenaming')):
            return False
        else:
            return True

    def doRename(self):
        '''
        Go find files and rename them!
        '''

        if self.isDisabled():
            return

        allFiles = self.findFiles()

        if allFiles:
            log.debug("Ready to rename some files.")

        for files in allFiles:

            # See if imdb link is in nfo file
            nfo = files.get('nfo')
            movie = {}
            if nfo:
                nfoFile = open(os.path.join(nfo.get('path'), nfo.get('filename')), 'r').read()
                imdbId = self.getImdb(nfoFile)
                if imdbId:
                    log.info('Found movie via nfo file.')
                    movie = {
                        'movie': self.getMovie(imdbId),
                        'queue': None
                    }
            # Try other methods
            if not movie:
                movie = self.determineMovie(files)

            if movie and movie.get('movie'):
                finalDestination = self.renameFiles(files, movie['movie'], movie['queue'])

                #Generate XBMC metadata
                if self.config.get('XBMC', 'metaEnabled'):
                    xmg.metagen(finalDestination['directory'],
                                imdb_id = movie['movie'].imdb,
                                fanart_min_height = self.config.get('XBMC', 'fanartMinHeight'),
                                fanart_min_width = self.config.get('XBMC', 'fanartMinWidth'))
                    log.info('XBMC metainfo for imdbid, %s, generated' % movie['movie'].imdb)

                if self.config.get('Trailer', 'quality'):
                    self.trailerQueue.put({'movieId': movie['movie'].id, 'destination':finalDestination})

                # Search for subtitles
                cherrypy.config['cron']['subtitle'].forDirectory(finalDestination['directory'])

                #Notify XBMC
                if self.config.get('XBMC', 'notify'):
                    xbmc.notifyXBMC('CouchPotato',
                                    'Downloaded %s (%s)' % (movie['movie'].name, movie['movie'].year),
                                    self.config.get('XBMC', 'host'),
                                    self.config.get('XBMC', 'username'),
                                    self.config.get('XBMC', 'password'))
                    log.info('XBMC notification sent to %s' % self.config.get('XBMC', 'host'))


                #Update XBMC Library
                if self.config.get('XBMC', 'updatelibrary'):
                    xbmc.updateLibrary(self.config.get('XBMC', 'host'),
                                       self.config.get('XBMC', 'username'),
                                       self.config.get('XBMC', 'password'))
                    log.info('XBMC library update initiated')

            else:
                try:
                    file = files['files'][0]
                    path = file['path'].split(os.sep)
                    path.extend(['_UNKNOWN_' + path.pop()])
                    shutil.move(file['path'], os.sep.join(path))
                except IOError:
                    pass

                log.info('No Match found for: %s' % str(files['files']))

        # Cleanup
        if self.conf('cleanup'):
            path = self.conf('download')

            if self.conf('destination') == path:
                log.error('Download folder and movie destination shouldn\'t be the same. Change it in Settings >> Renaming.')
                return

            for root, subfiles, filenames in os.walk(path):
                log.debug(subfiles)

                # Stop if something is unpacking
                if '_unpack' in root.lower() or '_failed_' in root.lower() or '_unknown_' in root.lower():
                    break

                for filename in filenames:
                    fullFilePath = os.path.join(root, filename)
                    fileSize = os.path.getsize(fullFilePath)

                    if fileSize < 157286400:
                        try:
                            os.remove(fullFilePath)
                            log.info('Removing file %s.' % fullFilePath)
                        except OSError:
                            log.error('Couldn\'t remove file' % fullFilePath)

                if not root in path:
                    try:
                        os.rmdir(root)
                        log.info('Removing dir: %s in download dir.' % root)
                    except OSError:
                        log.error('Tried to clean-up download folder, but "%s" isn\'t empty.' % root)

    def getQueue(self, movie):

        log.info('Finding quality for %s.' % movie.name)

        try:
            # Assuming quality is the top most, as that should be the last downloaded..
            for queue in movie.queue:
                if queue.name:
                    return queue

        except TypeError:
            return None

    def getSourceMedia(self, files):
        '''
        get source media ... durr
        '''
        for media in self.sourceMedia:
            for mediaAlias in self.sourceMedia[media]:
                for file in files['files']:
                    if mediaAlias in file['filename'].lower() or mediaAlias in file['path'].lower():
                        return media
        return None

    def renameFiles(self, files, movie, queue = None):
        '''
        rename files based on movie data & conf
        '''

        movieSourceMedia = self.getSourceMedia(files)
        multiple = False
        if len(files['files']) > 1:
            multiple = True

        destination = self.conf('destination')
        folderNaming = self.conf('foldernaming')
        fileNaming = self.conf('filenaming')

        # Remove weird chars from moviename
        moviename = re.sub(r"[\x00\/\\:\*\?\"<>\|]", '', movie.name)

        # Put 'The' at the end
        namethe = moviename
        if moviename[:3].lower() == 'the':
            namethe = moviename[3:] + ', The'

        #quality
        if not queue:
            queue = self.getQueue(movie)

        if not queue:
            quality = Qualities().guess(files['files'])
            queueId = 0
        else:
            quality = Qualities.types[queue.qualityType]['label']
            queueId = queue.id

        replacements = {
             'cd': '',
             'cdNr': '',
             'ext': '.mkv',
             'namethe': namethe.strip(),
             'thename': moviename.strip(),
             'year': movie.year,
             'first': namethe[0].upper(),
             'quality': quality,
        }
        if multiple:
            cd = 1

        justAdded = []

        totalSize = 0
        for file in files['files']:
            fullPath = os.path.join(file['path'], file['filename'])
            totalSize += os.path.getsize(fullPath)

            # Do something with ISO, as they should be between DVDRip and BRRIP
            ext = os.path.splitext(file['filename'])[1].lower()[1:]
            if ext == 'iso':
                totalSize -= (os.path.getsize(fullPath) / 1.6)
        log.info('Total size of new files is %s.' % int(totalSize / 1024 / 1024))

        finalDestination = None
        finalFilename = self.doReplace(fileNaming, replacements)

        for file in sorted(files['files']):
            log.info('Trying to find a home for: %s' % latinToAscii(file['filename']))

            replacements['ext'] = file['ext']

            if multiple:
                replacements['cd'] = ' cd' + str(cd)
                replacements['cdNr'] = ' ' + str(cd)

            replacements['original'] = file['root']
            replacements['video'] = self.getCodec(file['filename'], RenamerCron.videoCodecs)
            replacements['audio'] = self.getCodec(file['filename'], RenamerCron.audioCodecs)
            replacements['group'] = self.getGroup(file['root'])

            folder = self.doReplace(folderNaming, replacements)
            filename = self.doReplace(fileNaming, replacements)

            #insert source media into filename
            if self.config.get('XBMC', 'sourceRename') and movieSourceMedia:
                splitted = os.path.splitext(filename)
                if splitted[0][-1] == ".":
                    splitted = list(splitted)
                    splitted[0] = splitted[0][:-1]
                filename = "%s.%s%s" % (splitted[0], movieSourceMedia, splitted[1])

            old = os.path.join(file['path'], file['filename'])
            dest = os.path.join(destination, folder, filename)

            finalDestination = os.path.dirname(dest)
            if not os.path.isdir(finalDestination):

                # Use same permissions as conf('destination') folder
                try:
                    #mode = os.stat(destination)
                    #chmod = mode[ST_MODE] & 07777
                    log.info('Creating directory %s' % finalDestination)
                    os.makedirs(finalDestination)
                    shutil.copymode(destination, finalDestination)
                    #os.chmod(finalDestination, chmod)
                except OSError:
                    log.error('Failed setting permissions for %s' % finalDestination)
                    os.makedirs(finalDestination)

            # Remove old if better quality
            removed = self.removeOld(os.path.join(destination, folder), justAdded, totalSize)

            if not os.path.isfile(dest) and removed:
                log.info('Moving file "%s" to %s.' % (latinToAscii(old), dest))
                shutil.move(old, dest)
                justAdded.append(dest)
            else:
                try:
                    path = file['path'].split(os.sep)
                    path.extend(['_EXISTS_' + path.pop()])
                    shutil.move(file['path'], os.sep.join(path))
                except IOError:
                    pass
                log.error('File %s already exists or not better.' % latinToAscii(filename))
                break

            #get subtitle if any & move
            if len(files['subtitles']) > 0:
                log.info('Moving matching subtitle.')
                subtitle = files['subtitles'].pop(0)
                replacements['ext'] = subtitle['ext']
                subFilename = self.doReplace(fileNaming, replacements)
                shutil.move(os.path.join(subtitle['path'], subtitle['filename']), os.path.join(destination, folder, subFilename))

            # Add to renaming history
            h = RenameHistory()
            h.movieId = movie.id
            h.movieQueue = queueId
            h.old = unicode(old.decode('utf-8'))
            h.new = unicode(dest.decode('utf-8'))
            Db.add(h)
            Db.flush()

            if multiple:
                cd += 1

        # Mark movie downloaded
        if queueId > 0:
            if queue.markComplete:
                movie.status = u'downloaded'

            queue.completed = True
            Db.flush()

        return {
            'directory': finalDestination,
            'filename': finalFilename
        }

    def removeOld(self, path, dontDelete = [], newSize = 0):

        files = []
        oldSize = 0
        for root, subfiles, filenames in os.walk(path):
            log.debug(subfiles)

            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()[1:]
                fullPath = os.path.join(root, filename)
                oldSize += os.path.getsize(fullPath)

                # iso's are huge, but the same size as 720p, so remove some filesize for better comparison
                if ext == 'iso':
                    oldSize -= (os.path.getsize(fullPath) / 1.6)

                if not fullPath in dontDelete:

                    # Only delete media files and subtitles
                    if ('*.' + ext in self.movieExt or '*.' + ext in self.subExt) and not '-trailer' in filename:
                        files.append(fullPath)

        log.info('Quality Old: %s, New %s.' % (int(oldSize / 1024 / 1024), int(newSize / 1024 / 1024)))
        if oldSize < newSize:
            for file in files:
                try:
                    os.remove(file)
                    log.info('Removed old file: %s' % file)
                except OSError:
                    log.info('Couldn\'t delete file: %s' % file)
            return True
        else:
            log.info('New file(s) are smaller then old ones, don\'t overwrite')
            return False


    def doReplace(self, string, replacements):
        '''
        replace confignames with the real thing
        '''

        replaced = string
        for x, r in replacements.iteritems():
            replaced = replaced.replace('<' + x + '>', str(r))

        replaced = re.sub(r"[\x00:\*\?\"<>\|]", '', replaced)

        sep = self.conf('separator')
        return self.replaceDoubles(replaced).replace(' ', ' ' if not sep else sep)

    def replaceDoubles(self, string):
        return string.replace('  ', ' ').replace(' .', '.')

    def getMovie(self, imdbId):
        '''
        Get movie based on IMDB id.
        If not in local DB, go fetch it from theMovieDb
        '''

        movie = Db.query(Movie).filter_by(imdb = imdbId).first()

        if not movie:
            movie = self.searcher.get('movie').findByImdbId(imdbId)

        return movie

    def determineMovie(self, files):
        '''
        Try find movie based on folder names and MovieQueue table
        '''

        for file in files['files']:
            dirnames = file['path'].split(os.path.sep)
            dirnames.append(file['filename'])
            dirnames.reverse()

            for dir in dirnames:
                dir = latinToAscii(dir)

                # check and see if name is in queue
                queue = Db.query(MovieQueue).filter_by(name = dir).first()
                if queue:
                    log.info('Found movie via MovieQueue.')
                    return {
                        'queue': queue,
                        'movie': queue.Movie
                    }

                # last resort, match every word in path to db
                lastResort = {}
                dirSplit = re.split('\W+', dir.lower())
                for s in dirSplit:
                    if s:
                        results = Db.query(Movie).filter(Movie.name.like('%' + s + '%')).all()
                        for r in results:
                            lastResort[r.id] = r

                for l in lastResort.itervalues():
                    wordCount = 0
                    words = re.split('\W+', l.name.lower())
                    for word in words:
                        if word in dir.lower():
                            wordCount += 1

                    if wordCount == len(words) and len(words) > 0 and str(l.year) in dir:
                        log.info('Found via last resort searching.')
                        return {
                            'queue': None,
                            'movie': l
                        }
            # Try finding movie on theMovieDB
            # more checking here..

        return False

    def getImdb(self, txt):

        try:
            m = re.search('imdb.com/title/(?P<id>tt[0-9]+)', txt)
            id = m.group('id')
            if id:
                return id
        except AttributeError:
            return False

        return False

    def getCodec(self, filename, codecs):
        codecs = map(re.escape, codecs)
        try:
            codec = re.search('[^A-Z0-9](?P<codec>' + '|'.join(codecs) + ')[^A-Z0-9]', filename, re.I)
            return (codec and codec.group('codec')) or 'unknown'
            return 'unknown'
        except:
            log.info('Renaming: ' + traceback.format_exc())
            return 'Exception'

    def getGroup(self, filename):
        try:
            group = re.search('-(?P<group>[A-Z0-9]+)$', filename, re.I)
            return (group and group.group('group')) or 'unknown'
        except:
            log.info('Renaming: ' + traceback.format_exc())
            return 'Exception'

    def findFiles(self):

        files = []

        path = self.conf('download')
        for dir in os.listdir(path):
            fullDirPath = os.path.join(path, dir)

            for root, subfiles, filenames in os.walk(fullDirPath):

                subfiles = {'nfo':{}, 'files':[], 'subtitles':[]}

                patterns = []
                patterns.extend(self.movieExt)
                patterns.extend(self.nfoExt)
                patterns.extend(self.subExt)

                for pattern in patterns:
                    for filename in fnmatch.filter(filenames, pattern):
                        new = {
                           'path': root,
                           'filename': filename,
                           'root' : os.path.splitext(filename)[0],
                           'ext': os.path.splitext(filename)[1].lower()[1:], #[1:]to remove . from extension
                        }

                        #nfo file
                        if('*.' + new.get('ext') in self.nfoExt):
                            subfiles['nfo'] = new
                        #subtitle file
                        elif('*.' + new.get('ext') in self.subExt):
                            subfiles['subtitles'].append(new)
                        else:
                            #ignore movies files / or not
                            if not self.ignoreFile(os.path.join(root, filename)):
                                subfiles['files'].append(new)

                if subfiles['files']:
                    files.append(subfiles)

        return files

    def ignoreFile(self, file):

        if re.search('(^|[\W_])sample\d*[\W_]', file.lower()):
            return True

        # minimal size
        if os.path.getsize(file) < self.minimalFileSize:
            log.info('File to small.')
            return True

        # ignoredpaths
        for i in self.ignoredInPath:
            if i in file.lower():
                log.debug('File still unpacking.')
                return True

        # All is OK
        return False


def startRenamerCron(config, searcher, debug):
    cron = RenamerCron()
    cron.config = config
    cron.debug = debug
    cron.searcher = searcher
    cron.trailerQueue = searcher.get('trailerQueue')
    cron.start()

    return cron
