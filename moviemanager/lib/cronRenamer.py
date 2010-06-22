
from moviemanager.model import Movie, History, RenameHistory
from moviemanager.model.meta import Session as Db
import Queue
import logging
import threading
import time
import os
import fnmatch
import re

log = logging.getLogger(__name__)

class RenamerCron(threading.Thread):

    ''' Cronjob for renaming movies '''

    interval = 1 #minutes
    intervalSec = 10
    config = {}
    minimalFileSize = 1024 * 1024 * 10 # 10MB
    ignoredInPath = ['_unpack', '.appledouble', '/._'] #unpacking, smb-crap

    def run(self):
        log.info('Renamer thread is running.')

        self.intervalSec = (self.interval * 60)

        #sleep longer if renaming is disabled
        if self.config.get('enabled').lower() != 'true':
            log.info('Sleeping renaming thread');
            self.intervalSec = 36000

        if not os.path.isdir(self.config.get('download')):
            log.info("Watched folder doesn't exist.")

        time.sleep(10)
        while True:

            #check all movies
            now = time.time()

            self.doRename()

            log.info('Sleeping RenamingCron for %d minutes.' % self.interval)
            time.sleep(self.intervalSec)

    def isDisabled(self):

        if (self.config.get('enabled').lower() == 'true' and os.path.isdir(self.config.get('download')) and self.config.get('download') and self.config.get('destination') and self.config.get('foldernaming') and self.config.get('filenaming')):
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
                self.renameFiles(files, movie)
            else:
                log.error('Renamer: No movie match found.')

    def renameFiles(self, files, movie):
        '''
        rename files based on movie data en config
        '''

        multiple = False
        if len(files['files']) > 1:
            multiple = True

        destination = self.config.get('destination')
        folderNaming = self.config.get('foldernaming')
        fileNaming = self.config.get('filenaming')

        # Remove weird chars from moviename
        moviename = replaced = re.sub(r"[\x00\/\\:\*\?\"<>\|]", '', movie.name)

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

        for file in files['files']:

            replacements['ext'] = file['ext']

            if multiple:
                replacements['cd'] = ' cd' + str(cd)
                replacements['cdNr'] = ' ' + str(cd)
                cd += 1

            folder = self.doReplace(folderNaming, replacements)
            filename = self.doReplace(fileNaming, replacements)

            old = os.path.join(file['path'], file['filename'])
            dest = os.path.join(destination, 'test', folder, filename)

            log.info('Moving file "%s" to %s.' % (old, dest))
            if not os.path.isdir(os.path.split(dest)[0]):
                os.makedirs(os.path.split(dest)[0])

            if not os.path.isfile(dest):
                os.rename(old, dest)
            else:
                log.error('File %s already exists.' % filename)
                break
            
            # Add to renaming history
            h = RenameHistory()
            h.movieId = movie.id
            h.old = old
            h.new = dest
            Db.add(h)
            Db.commit()
        
        # Mark movie downloaded
        movie.status = u'downloaded'
        Db.commit()

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
            from moviemanager.lib.provider.theMovieDb import theMovieDb
            movie = theMovieDb.findByImdbId(imdb)

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
                print dir
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

        path = self.config.get('download')
        for dir in os.listdir(path):
            fullDirPath = os.path.join(path, dir)

            for root, dirnames, filenames in os.walk(fullDirPath):

                subfiles = {'nfo':{}, 'files':[]}

                patterns = ['*.mkv', '*.wmv', '*.avi', '*.mpg', '*.mpeg', '*.mp4', '*.m2ts', '*.iso', '*.nfo']
                for pattern in patterns:
                    for filename in fnmatch.filter(filenames, pattern):

                        new = {
                           'path': root,
                           'filename': filename,
                           'ext': os.path.splitext(filename)[1].lower()[1:]
                        }

                        if(new.get('ext') == 'nfo'):
                            subfiles['nfo'] = new
                        else:

                            #ignore
                            if not self.ignoreFile(os.path.join(root, filename)):
                                subfiles['files'].append(new)

                if subfiles['files']:
                    files.append(subfiles)

        return files

    def ignoreFile(self, file):

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


def startRenamerCron(config):
    cron = RenamerCron()
    cron.config = config
    cron.start()

    return cron
