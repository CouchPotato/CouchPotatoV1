from app import latinToAscii
from app.config.cplog import CPLog
from app.config.db import Movie, Session as Db, MovieQueue
import fnmatch
import os
import re

log = CPLog(__name__)

class Library:

    minimalFileSize = 1024 * 1024 * 200 # 10MB
    ignoredInPath = ['_unpack', '_failed_', '_unknown_', '_exists_', '.appledouble', '/._', '/.'] #unpacking, smb-crap, hidden files
    extensions = {
        'movie': ['*.mkv', '*.wmv', '*.avi', '*.mpg', '*.mpeg', '*.mp4', '*.m2ts', '*.iso'],
        'nfo': ['*.nfo'],
        'subtitle': ['*.sub', '*.srt', '*.idx', '*.ssa', '*.ass'],
        'trailer': ['*.mov', '*.mp4', '*.flv']
    }

    def getMovies(self, folder = None):

        movies = []

        movieFolder = folder if folder else self.config.get('Renamer', 'destination')
        if not os.path.isdir(movieFolder):
            log.error('Can\'t find directory: %s' % movieFolder)
            return movies

        for root, subfiles, filenames in os.walk(movieFolder):

            movie = {
                'movie': None,
                'history': None,
                'path': root,
                'folder': root.split(os.path.sep)[-1:].pop(),
                'nfo':[], 'files':[], 'subtitles':[], 'trailer':[]
            }

            patterns = []
            for extType in self.extensions.itervalues():
                patterns.extend(extType)

            for pattern in patterns:
                for filename in fnmatch.filter(filenames, pattern):
                    fullFilePath = os.path.join(root, filename)
                    new = {
                       'filename': filename,
                       'ext': os.path.splitext(filename)[1].lower()[1:], #[1:]to remove . from extension
                    }

                    #nfo file
                    if('*.' + new.get('ext') in self.extensions['nfo']):
                        movie['nfo'].append(filename)
                    #subtitle file
                    elif('*.' + new.get('ext') in self.extensions['subtitle']):
                        movie['subtitles'].append(new)
                    #trailer file
                    elif re.search('(^|[\W_])trailer\d*[\W_]', filename.lower()) and self.filesizeBetween(fullFilePath, 2, 250):
                        movie['trailer'].append(new)
                    else:
                        #ignore movies files / or not
                        if self.keepFile(fullFilePath):
                            movie['files'].append(new)

            if movie['files']:
                # Find movie by nfo
                if movie['nfo']:
                    for nfo in movie['nfo']:
                        nfoFile = open(os.path.join(movie['path'], nfo), 'r').read()
                        imdbId = self.getImdb(nfoFile)
                        if imdbId:
                            movie['movie'] = self.getMovieByIMDB(imdbId)

                # Find movie via files
                if not movie['movie']:
                    movie['movie'] = self.determineMovie(movie)

                if movie['movie']:
                    movie['history'] = self.getHistory(movie['movie'])

                movies.append(movie)

        return movies

    def getHistory(self, movie):

        for queue in movie.queue:
            if queue.renamehistory and queue.renamehistory[0]:
                return queue.renamehistory

        return None

    def determineMovie(self, movie):


        for file in movie['files']:
            dirnames = movie['path'].split(os.path.sep)
            dirnames.append(file['filename'])
            dirnames.reverse()

            for dir in dirnames:
                dir = latinToAscii(dir)

                # check and see if name is in queue
                queue = Db.query(MovieQueue).filter_by(name = dir).first()
                if queue:
                    log.info('Found movie via MovieQueue.')
                    return queue.Movie

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
                        return l

        return None

    def getImdb(self, txt):
        try:
            m = re.search('(?P<id>tt[0-9{7}]+)', txt)
            id = m.group('id')
            if id:
                return id
        except AttributeError:
            return False

        return False

    def getMovieByIMDB(self, imdbId):
        '''
        Get movie based on IMDB id.
        If not in local DB, go fetch it from theMovieDb
        '''
        return Db.query(Movie).filter_by(imdb = imdbId).first()

    def filesizeBetween(self, file, min = 0, max = 100000):
        try:
            return (min * 1048576) < os.path.getsize(file) < (max * 1048576)
        except:
            log.error('Couln\'t get filesize of %s.' % file)

        return False

    def keepFile(self, file):

        # ignoredpaths
        for i in self.ignoredInPath:
            if i in file.lower():
                log.debug('Path contains " %s ".' % i)
                return False

        # Sample file
        if re.search('(^|[\W_])sample\d*[\W_]', file.lower()):
            return False

        # Minimal size
        if self.filesizeBetween(file, self.minimalFileSize):
            log.info('File to small: %s' % file)
            return False

        # All is OK
        return True
