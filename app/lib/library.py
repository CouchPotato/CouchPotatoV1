from app import latinToAscii
from app.config.cplog import CPLog
from app.config.db import Movie, Session as Db, MovieQueue
from app.lib import hashFile
from app.lib.qualities import Qualities

import hachoir_metadata
import hachoir_parser

import cherrypy
import fnmatch
import os
import re

#temporary imports until figure out hachoir file locking
import base64
import subprocess

log = CPLog(__name__)

class Library:

    def __init__(self):
        self.config = cherrypy.config.get('config')

    minimalFileSize = 1024 * 1024 * 200 # 10MB
    ignoredInPath = ['_unpack', '_failed_', '_unknown_', '_exists_', '.appledouble', '/._', '/.'] #unpacking, smb-crap, hidden files
    extensions = {
        'movie': ['*.mkv', '*.wmv', '*.avi', '*.mpg', '*.mpeg', '*.mp4', '*.m2ts', '*.iso'],
        'nfo': ['*.nfo'],
        'subtitle': ['*.sub', '*.srt', '*.ssa', '*.ass'],
        'subtitleExtras': ['*.idx'],
        'trailer': ['*.mov', '*.mp4', '*.flv']
    }
    codecs = {
        'audio': ['dts', 'ac3', 'ac3d', 'mp3'],
        'video': ['x264', 'divx', 'xvid']
    }

    sourceMedia = { 'bluray': ['bluray', 'blu-ray', 'brrip', 'br-rip'],
                    'hddvd': ['hddvd', 'hd-dvd'],
                    'dvd': ['dvd'],
                    'hdtv': ['hdtv']}

    # From Plex/XBMC
    clean = '(?i)[^\s]*(ac3|dts|custom|dc|divx|divx5|dsr|dsrip|dutch|dvd|dvdrip|dvdscr|dvdscreener|screener|dvdivx|cam|fragment|fs|hdtv|hdrip|hdtvrip|internal|limited|multisubs|ntsc|ogg|ogm|pal|pdtv|proper|repack|rerip|retail|r3|r5|bd5|se|svcd|swedish|german|read.nfo|nfofix|unrated|ws|telesync|ts|telecine|tc|brrip|bdrip|480p|480i|576p|576i|720p|720i|1080p|1080i|hrhd|hrhdtv|hddvd|bluray|x264|h264|xvid|xvidvd|xxx|www.www|cd[1-9]|\[.*\])[^\s]*'
    multipartRegEx = [
        '[ _\.-]+cd[ _\.-]*([0-9a-d]+)', #*cd1
        '[ _\.-]+dvd[ _\.-]*([0-9a-d]+)', #*dvd1
        '[ _\.-]+part[ _\.-]*([0-9a-d]+)', #*part1.mkv
        '[ _\.-]+dis[ck][ _\.-]*([0-9a-d]+)', #*disk1.mkv
        '()[ _\.-]+([0-9]*[abcd]+)(\.....?)$',
        '([a-z])([0-9]+)(\.....?)$',
        '()([ab])(\.....?)$' #*a.mkv 
    ]
    noTables = False

    def getMovies(self, folder = None):

        movies = []
        qualities = Qualities()

        movieFolder = unicode(folder if folder else self.config.get('Renamer', 'destination'))
        if not os.path.isdir(movieFolder):
            log.error('Can\'t find directory: %s' % movieFolder)
            return movies

        for root, subfiles, filenames in os.walk(movieFolder):
            if self.abort:  return movies

            movie = {
                'movie': None,
                'queue': 0,
                'match': False,
                'info': {
                    'name': None,
                    'year': None,
                    'quality': '',
                    'resolution': None,
                    'sourcemedia': '',
                    'size': 0,
                    'codec': {
                        'video': '',
                        'audio': ''
                    },
                    'group': ''
                },
                'history': None,
                'path': root,
                'folder': root.split(os.path.sep)[-1:].pop(),
                'nfo':[], 'files':[], 'trailer':[],
                'subtitles':{
                    'files': [],
                    'extras': []
                }
            }

            patterns = []
            for extType in self.extensions.itervalues():
                patterns.extend(extType)

            for pattern in patterns:
                for filename in fnmatch.filter(sorted(filenames), pattern):
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
                        movie['subtitles']['files'].append(new)
                    #idx files
                    elif('*.' + new.get('ext') in self.extensions['subtitleExtras']):
                        movie['subtitles']['extras'].append(new)
                    #trailer file
                    elif re.search('(^|[\W_])trailer\d*[\W_]', filename.lower()) and self.filesizeBetween(fullFilePath, 2, 250):
                        movie['trailer'].append(new)
                    else:
                        #ignore movies files / or not
                        if self.keepFile(fullFilePath):
                            new['hash'] = hashFile(fullFilePath) # Add movie hash
                            new['size'] = os.path.getsize(fullFilePath) # File size
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

                    movie['match'] = True
                    movie['info']['name'] = movie['movie'].name
                    movie['info']['year'] = movie['movie'].year
                    try:
                        movie['info']['quality'] = movie['history'].movieQueue.qualityType
                    except:
                        movie['info']['quality'] = qualities.guess([os.path.join(movie['path'], file['filename']) for file in movie['files']])

                    for file in movie['files']:
                        movie['info']['size'] += file['size']

                    movie['info']['size'] = str(movie['info']['size'])
                    movie['info']['group'] = self.getGroup(movie['folder'])
                    movie['info']['codec']['video'] = self.getCodec(movie['folder'], self.codecs['video'])
                    movie['info']['codec']['audio'] = self.getCodec(movie['folder'], self.codecs['audio'])

                    #check the video file for it's resolution
                    test_file = os.path.join(movie['path'], movie['files'][0]['filename'])
                    resolution = self.getVideoResolution(test_file)
                    if resolution:
                        if (resolution[0] > 1900 or resolution[0] < 2000) and resolution[1] <= 1080:
                            named_resolution = '1080p'
                        elif (resolution[0] > 1200 or resolution[0] < 1300) and resolution[1] <= 720:
                            named_resolution = '720p'
                        else:
                            named_resolution = None
                    else:
                        named_resolution = None
                    movie['info']['resolution'] = named_resolution
                    movie['info']['sourcemedia'] = self.getSourceMedia(test_file)

                # Create filename without cd1/cd2 etc
                movie['filename'] = self.removeMultipart(os.path.splitext(movie['files'][0]['filename'])[0])

                # Give back ids, not table rows
                if self.noTables:
                    movie['history'] = [h.id for h in movie['history']] if movie['history'] else movie['history']
                    movie['movie'] = movie['movie'].id if movie['movie'] else movie['movie']

                movies.append(movie)

        return movies

    def removeMultipart(self, name):
        for regex in self.multipartRegEx:
            try:
                found = re.sub(regex, '', name)
                if found != name:
                    return found
            except:
                pass
        return name

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

        # Search tMDB
        movieName = self.cleanName(movie['folder'])
        if movieName:
            log.info('Searching for "%s".' % movieName)
            result = cherrypy.config['searchers']['movie'].find(movieName, limit = 1)
            if result:
                movie = self.getMovieByIMDB(result.imdb.replace('tt', ''))

                if not movie:
                    new = Movie()
                    Db.add(new)

                    try:
                        # Add found movie as downloaded
                        new.status = u'downloaded'
                        new.name = result.name
                        new.imdb = result.imdb
                        new.movieDb = result.id
                        new.year = result.year
                        Db.flush()

                        return new
                    except Exception, e:
                        log.error('Movie could not be added to database %s. %s' % (result, e))

        return None

    def cleanName(self, text):
        cleaned = ' '.join(re.split('\W+', text.lower()))
        cleaned = re.sub(self.clean, ' ', cleaned)
        year = self.findYear(cleaned)

        if year: # Split name on year
            try:
                movieName = cleaned.split(year).pop(0).strip()
                return movieName + ' ' + year
            except:
                pass
        else: # Split name on multiple spaces
            try:
                movieName = cleaned.split('  ').pop(0).strip()
                return movieName
            except:
                pass

        return None

    def findYear(self, text):
        matches = re.search('(?P<year>[0-9]{4})', text)
        if matches:
            return matches.group('year')

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

    def getCodec(self, filename, codecs):
        codecs = map(re.escape, codecs)
        try:
            codec = re.search('[^A-Z0-9](?P<codec>' + '|'.join(codecs) + ')[^A-Z0-9]', filename, re.I)
            return (codec and codec.group('codec')) or ''
        except:
            return ''

    def getGroup(self, filename):
        try:
            group = re.search('-(?P<group>[A-Z0-9]+)$', filename, re.I)
            return (group and group.group('group')) or ''
        except:
            return ''

    def getSourceMedia(self, file):
        '''
        get source media from filename... durr
        '''

        #TODO: handle filenames that have multiple source medias in them
        medias = []
        for media in self.sourceMedia:
            for mediaAlias in self.sourceMedia[media]:
                if mediaAlias in file.lower() or mediaAlias in file.lower():
                    medias.append(media)

        try:
            return medias[0]
        except:
            return None

    def getVideoResolution(self, file):
        '''
        Using hachoir_metadata we look at the video file and get the horizontal resolution and return the appropriate
        resolution string (1080p, 720p)

        Currently we return None for less than 720p
        '''
#        file = unicode(file)
#        parser = hachoir_parser.createParser(file)
#        metadata = hachoir_metadata.extractMetadata(parser)
#
#        for md in metadata.iterGroups():
#            if md.has("height") and md.has("width"):
#                return md.get("width"), md.get("height")
#
#        return None

        return self._get_res(file)

    def _get_res(self, filename):
        '''
        A hacky way to keep hachoir from locking the file so that we can actually move it after
        getting metadata.  This is temporary.
        '''
        temp_file_contents = '''
        ZnJvbSBoYWNob2lyX3BhcnNlciBpbXBvcnQgY3JlYXRlUGFyc2VyCmZyb20gaGFjaG9pcl9tZXRhZGF0
        YSBpbXBvcnQgZXh0cmFjdE1ldGFkYXRhCmltcG9ydCBzeXMKCmRlZiBnZXRWaWRlb1Jlc29sdXRpb24o
        ZmlsZSk6CiAgICAgICAgJycnCiAgICAgICAgVXNpbmcgaGFjaG9pcl9tZXRhZGF0YSB3ZSBsb29rIGF0
        IHRoZSB2aWRlbyBmaWxlIGFuZCBnZXQgdGhlIGhvcml6b250YWwgcmVzb2x1dGlvbiBhbmQgcmV0dXJu
        IHRoZSBhcHByb3ByaWF0ZQogICAgICAgIHJlc29sdXRpb24gc3RyaW5nICgxMDgwcCwgNzIwcCkKCiAg
        ICAgICAgQ3VycmVudGx5IHdlIHJldHVybiBOb25lIGZvciBsZXNzIHRoYW4gNzIwcAogICAgICAgICcn
        JwogICAgICAgIGZpbGUgPSB1bmljb2RlKGZpbGUpCiAgICAgICAgcGFyc2VyID0gY3JlYXRlUGFyc2Vy
        KGZpbGUpCiAgICAgICAgbWV0YWRhdGEgPSBleHRyYWN0TWV0YWRhdGEocGFyc2VyKQoKICAgICAgICB0
        cnk6CiAgICAgICAgICAgIGlmIG1ldGFkYXRhOgogICAgICAgICAgICAgICAgZm9yIG1kIGluIG1ldGFk
        YXRhLml0ZXJHcm91cHMoKToKICAgICAgICAgICAgICAgICAgICBpZiBtZC5oYXMoImhlaWdodCIpIGFu
        ZCBtZC5oYXMoIndpZHRoIik6CiAgICAgICAgICAgICAgICAgICAgICAgIHJldHVybiBtZC5nZXQoIndp
        ZHRoIiksIG1kLmdldCgiaGVpZ2h0IikKICAgICAgICBleGNlcHQ6CiAgICAgICAgICAgIHBhc3MKCgpy
        ZXMgPSBnZXRWaWRlb1Jlc29sdXRpb24oc3lzLmFyZ3ZbMV0pCmlmIHJlczoKICAgIHByaW50IHJlc1sw
        XQogICAgcHJpbnQgcmVzWzFdCmVsc2U6CiAgICBwcmludCAnZXJyb3In
        '''

        library_dir = os.path.abspath(os.path.split(os.path.dirname(hachoir_parser.__file__))[0])
        dest_file = os.path.join(library_dir, 'tempresgetter.py')
        f=open(dest_file, 'w')
        f.write(base64.b64decode(temp_file_contents))
        f.close()

        script = os.path.abspath(dest_file)

        library_dir = os.path.abspath(os.path.split(os.path.dirname(hachoir_parser.__file__))[0])

        p = subprocess.Popen(["python", script, filename], stdout=subprocess.PIPE, cwd = library_dir)
        z = p.communicate()[0]
#        import pdb; pdb.set_trace()
        os.remove(dest_file)

        try:
            z = [int(x.strip()) for x in z.split("\n") if x.strip() is not '']
        except:
            return None

        return z

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
