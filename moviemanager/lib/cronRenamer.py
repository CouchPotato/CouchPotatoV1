from moviemanager.lib.cronBase import cronBase
from moviemanager.model import Movie, History, RenameHistory
from moviemanager.model.meta import Session as Db
import fnmatch
import logging
import os
import re
import time

log = logging.getLogger(__name__)

class RenamerCron(cronBase):

    ''' Cronjob for renaming movies '''

    interval = 1 #minutes
    intervalSec = 10
    config = {}
    trailer = {}
    minimalFileSize = 1024 * 1024 * 10 # 10MB
    ignoredInPath = ['_unpack', '.appledouble', '/._'] #unpacking, smb-crap

    def conf(self, option):
        return self.config.get('Renamer', option)

    def run(self):
        log.info('Renamer thread is running.')

        self.intervalSec = (self.interval * 60)

        #sleep longer if renaming is disabled
        if self.conf('enabled').lower() != 'true':
            log.info('Sleeping renaming thread');
            self.intervalSec = 36000

        if not os.path.isdir(self.conf('download')):
            log.info("Watched folder doesn't exist.")

        time.sleep(10)
        while True and not self.abort:
            self.running = True
            self.doRename()
            self.running = False
            time.sleep(self.intervalSec)

        log.info('Renamer has shutdown.')

    def isDisabled(self):

        if (self.conf('enabled').lower() == 'true' and os.path.isdir(self.conf('download')) and self.conf('download') and self.conf('destination') and self.conf('foldernaming') and self.conf('filenaming')):
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

        for files in allFiles:

            # See if imdb link is in nfo file
            nfo = files.get('nfo')
            if nfo:
                nfoFile = open(os.path.join(nfo.get('path'), nfo.get('filename')), 'r').read()
                imdbId = self.getImdb(nfoFile)
                if imdbId:
                    log.info('Found movie via nfo file.')
                    movie = self.getMovie(imdbId)
            # Try other methods
            else:
                movie = self.determineMovie(files)

            if movie:
                finalDestination = self.renameFiles(files, movie)
                self.trailerQueue.put({'id': movie.imdb, 'movie': movie, 'destination':finalDestination})
            else:
                log.info('No Match found for: %s' % str(files['files']))

    def renameFiles(self, files, movie):
        '''
        rename files based on movie data & conf
        '''

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

        replacements = {
             'cd': '',
             'cdNr': '',
             'ext': '.mkv',
             'namethe': namethe.strip(),
             'thename': moviename.strip(),
             'year': movie.year,
             'first': namethe[0].upper()
        }
        if multiple:
            cd = 1

        finalDestination = None
        for file in files['files']:

            replacements['ext'] = file['ext']

            if multiple:
                replacements['cd'] = ' cd' + str(cd)
                replacements['cdNr'] = ' ' + str(cd)

            folder = self.doReplace(folderNaming, replacements)
            filename = self.doReplace(fileNaming, replacements)

            old = os.path.join(file['path'], file['filename'])
            dest = os.path.join(destination, folder, filename)

            log.info('Moving file "%s" to %s.' % (old, dest))
            if not os.path.isdir(os.path.split(dest)[0]):
                os.makedirs(os.path.split(dest)[0])

            if not os.path.isfile(dest):
                os.rename(old, dest)
            else:
                log.error('File %s already exists.' % filename)
                break

            #get subtitle if any & move
            if len(files['subtitles']) > 0:
                log.info('Moving matching subtitle.')
                subtitle = files['subtitles'].pop(0)
                replacements['ext'] = subtitle['ext']
                subFilename = self.doReplace(fileNaming, replacements)
                os.rename(os.path.join(subtitle['path'], subtitle['filename']), os.path.join(destination, folder, subFilename))

            # Add to renaming history
            h = RenameHistory()
            h.movieId = movie.id
            h.old = old
            h.new = dest
            Db.add(h)
            Db.commit()

            finalDestination = os.path.join(destination, folder)

            if multiple:
                cd += 1

        # Mark movie downloaded
        movie.status = u'downloaded'
        Db.commit()

        return finalDestination

    def doReplace(self, string, replacements):
        '''
        replace confignames with the real thing
        '''

        replaced = string
        for x, r in replacements.iteritems():
            replaced = replaced.replace('<' + x + '>', str(r))

        replaced = re.sub(r"[\x00:\*\?\"<>\|]", '', replaced)

        return replaced

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
        Try find movie based on folder names and History table
        '''

        for file in files['files']:
            dirnames = file['path'].split(os.path.sep)
            dirnames.append(file['filename'])
            dirnames.reverse()

            for dir in dirnames:
                # check and see if name is in history
                history = Db.query(History).filter_by(name = dir).first()
                if history:
                    log.info('Found movie via History.')
                    return history.movie

                # last resort, match every word in path to db
                lastResort = {}
                dir = dir.replace('.', ' ').lower()
                dirSplit = dir.split(' ')
                for s in dirSplit:
                    if s:
                        results = Db.query(Movie).filter(Movie.name.like('%' + s + '%')).all()
                        for r in results:
                            lastResort[r.id] = r

                for x in lastResort:
                    l = lastResort[x]
                    wordCount = 0
                    words = l.name.lower().split(' ')
                    for word in words:
                        if word.lower() in dir:
                            wordCount += 1

                    if wordCount == len(words) and len(words) > 0:
                        log.info('Found via last resort searching.')
                        return l
            # Try finding movie on theMovieDB
            # more checking here..

        return False

    def getImdb(self, txt):
        m = re.search('imdb.com/title/(?P<id>tt[0-9]+)', txt)
        id = m.group('id')
        if id:
            return id

        return False

    def findFiles(self):

        files = []

        path = self.conf('download')
        for dir in os.listdir(path):
            fullDirPath = os.path.join(path, dir)

            for root, subfiles, filenames in os.walk(fullDirPath):

                subfiles = {'nfo':{}, 'files':[], 'subtitles':[]}

                movieExt = ['*.mkv', '*.wmv', '*.avi', '*.mpg', '*.mpeg', '*.mp4', '*.m2ts', '*.iso']
                nfoExt = ['*.nfo']
                subExt = ['*.sub', '*.srt', '*.idx', '*.ssa', '*.ass']

                patterns = []
                patterns.extend(movieExt)
                patterns.extend(nfoExt)
                patterns.extend(subExt)

                for pattern in patterns:
                    for filename in fnmatch.filter(filenames, pattern):

                        new = {
                           'path': root,
                           'filename': filename,
                           'ext': os.path.splitext(filename)[1].lower()[1:]
                        }

                        #nfo file
                        if('*.' + new.get('ext') in nfoExt):
                            subfiles['nfo'] = new
                        #subtitle file
                        elif('*.' + new.get('ext') in subExt):
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
                log.info('File still unpacking.')
                return True

        # All is OK
        return False


def startRenamerCron(config, searcher, trailerQueue):
    cron = RenamerCron()
    cron.config = config
    cron.searcher = searcher
    cron.trailerQueue = trailerQueue
    cron.start()

    return cron
