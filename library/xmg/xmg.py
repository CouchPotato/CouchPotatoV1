import json
import os
import shutil
import urllib2

__author__ = 'Therms'
__tmdb_apikey__ = '6d96a9efb4752ed0d126d94e12e52036'

try:
    import imdb
    __imdb__ = True
except:
    __imdb__ = False

class XmgException(Exception):
    pass

class ApiError(XmgException):
    pass

class IdError(XmgException):
    pass

class NfoError(XmgException):
    pass

def metagen(location, fanart_min_height = 0, fanart_min_width = 0, poster_min_height = 0, poster_min_width = 0, name=None, imdb_id=None, tmdb_id=None, imdbpy=None):
    ''' metagen is used to download metadata for a movie or tv show and then create
    the necessary files for the media to be imported into XBMC.

    Arguments
    ===========
    location:  location should either be the full path/filename for the file you
    wish to generate metadata for, or in the case of multi-file movies/shows
    the full path/dir to the files.

    The remaining arguments are all potentially optional.

    fanart_height/width_min:  Sets lowest acceptable resolution fanart.  0 means
    disregard.  If no fanart available at specified resolution or greater, then
    we disregard this setting, and download highest resolution that is available.

    name*:  In the case of a movie, ideally this should be the full movie name
    followed by the year of the movie in parentheses. e.g. "The Matrix (1999)".
    If this is specific enough to generate only one search result then we'll
    continue. Otherwise, we'll raise IdError.

    Because of the imprecise nature of this method of id, only use it if you
    don't have the imdb_id or tmdb_id

    imdb_id:  Use this argument if you know the imdb id of the show/movie.  If
    this is used, the tmdb_id argument is ignored.

    tmdb_id*:  Use this argument if you know the tmdb id of the movie.  If this
    is used, the imdb_id argument is ignored.

    imdbpy:  When xmg is used as a library, imdbpy may not be installed
    system-wide, but included with your application.  If this is the case, pass
    your instance of imdb.IMDb() to metagen, so we can use it.

    *  These arguments are not yet supported.

    Notes
    ===========
    While there are python tmdb api libraries available, we've made the decision
    to access the tmdb api with our own methods.  The tmdb api is so simple, it
    requires very little code to implement.
    '''
    #first we'll evaluate our arguments for error conditions
    if not imdbpy and not __imdb__:
        raise ApiError("Can't import imdb and wasn't provided with an imdbpy instance")

    if os.path.isfile(location):
        isfile = True
        isdir = False
        location_dir = os.path.dirname(location)
    else:
        isfile = False
        if os.path.isdir(location):
            isdir = True
            location_dir = location
        else:
            raise ValueError("location must specify a file or a directory containing files to analyze")

    #housekeeping
    if imdbpy:
        i = imdbpy
    else:
        i = imdb.IMDb()

    #get an imdbpy movie object
    if imdb_id:
        if imdb_id[:2].lower() == 'tt':
            imdb_id = imdb_id[2:]

        try:
            imdbpy_movie = i.get_movie(imdb_id)
        except imdb._exceptions.IMDbParserError:
            raise IdError("%s is not a valid imdb id" % imdb_id)

        if len(imdbpy_movie.keys()) == 0:
            raise IdError("%s is not a valid imdb id" % imdb_id)
    #TODO: Search by movie name
    #TODO: Search by tmdb_id
    #TODO: Search by movie hash

    write_nfo(nfo_gen(imdbpy_movie, i), location_dir)
    get_fanart(imdb_id, location_dir, fanart_min_height, fanart_min_width)
    get_poster(imdb_id, location_dir, poster_min_height, poster_min_width)


def nfo_gen(imdbpy_movie, imdbpy):
    ''' Get the imdb url for the specified movie object
    '''
    nfo = imdbpy.get_imdbURL(imdbpy_movie)
    #TODO: Generate full nfo XML
    return nfo

def get_tmdb_imdb(imdb_id):
    url = "http://api.themoviedb.org/2.1/Movie.imdbLookup/en/json/%s/%s" % (__tmdb_apikey__, "tt" + imdb_id)
    response = urllib2.urlopen(url)
    data = json.loads(response.read())[0]
    return data


def get_fanartlist(imdb_id):
    ''' Returns a list of image urls from TMDb.
    '''
    data = get_tmdb_imdb(imdb_id)
    data = [image['image'] for image in data['backdrops'] if image['image'].get('size') == 'original']

    return data

def get_posterlist(imdb_id):
    ''' Returns a list of image urls from TMDb.
    '''
    data = get_tmdb_imdb(imdb_id)
    data = [image['image'] for image in data['posters'] if image['image'].get('size') == 'original']

    return data

def get_fanart(imdb_id, dir, min_height, min_width):
    '''  Fetches the fanart for the specified imdb_id and saves it to dir.
    Arguments

    min_height/width: Sets lowest acceptable resolution fanart.  0 means
    disregard.  If no fanart available at specified resolution or greater, then
    we disregard.
    '''

    fanarts = get_fanartlist(imdb_id)

    if len(fanarts) == 0:
        return

    fanart = get_image(fanarts, min_height, min_width)

    #fetch and write to disk
    dest = os.path.join(dir, "fanart%s" % os.path.splitext(fanart['url'])[-1])
    try:
        f = open(dest, 'wb')
    except:
        raise IOError("Can't open for writing: %s" % dest)

    response = urllib2.urlopen(fanart['url'])
    f.write(response.read())

    return True

def get_poster(imdb_id, dir, min_height, min_width):
    '''  Fetches the poster for the specified imdb_id and saves it to dir.
    Arguments

    min_height/width: Sets lowest acceptable resolution poster.  0 means
    disregard.  If no poster available at specified resolution or greater, then
    we disregard.
    '''
    posters = get_posterlist(imdb_id)
    if len(posters) == 0:
        return False

    poster = get_image(posters, min_height, min_width)
    dest = os.path.join(dir, "movie.tbn")
    try:
        f = open(dest, 'wb')
    except:
        raise IOError("Can't open for writing: %s" % dest)

    response = urllib2.urlopen(poster['url'])
    f.write(response.read())

    return True

def get_image(image_list, min_height, min_width):
    #Select image
    images = []
    for image in image_list:
        if not min_height or min_width:
                images.append(image)
                break
        elif min_height and not min_width:
            if image['height'] >= min_height:
                images.append(image)
                break
        elif min_width and not min_height:
            if image['width'] >= min_width:
                images.append(image)
                break
        elif min_width and min_height:
            if image['width'] >= min_width and image['height'] >= min_height:
                images.append(image)
                break

    #No image meets our resolution requirements, so disregard those requirements
    if len(images) == 0 and min_height or min_width:
        images.append(image_list[0])

    return images[0]


def write_nfo(nfo, dir):
    '''  Writes nfo to disk in a file called 'movie.nfo' in directory dir
    '''
    dest = os.path.join(dir, "movie.nfo")
    if os.path.isfile(dest):
        shutil.move(dest, "%s.bak" % dest)
    try:
        f = open(dest, 'w')
        f.write(nfo)
        f.close()
    except:
        raise NfoError("Couldn't write nfo")

def get_MPAA(movie_obj = None, imdb_id = None):

    pass

def get_imdbpy(imdbpy=False):
    if not imdbpy:
        return imdb.IMDb()
    else:
        return imdbpy

if __name__ == "__main__":
    import sys
    try:
        id = sys.argv[1]
    except:
        print "Type '%s _IMDBID_' to generate metadata." % sys.argv[0]
        sys.exit()

    metagen(os.getcwd(), imdb_id = id )
