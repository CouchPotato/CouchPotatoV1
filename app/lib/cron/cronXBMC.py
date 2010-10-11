import xml.etree.ElementTree as XMLTree

from app.lib.provider.movie.sources.imdbWrapper import imdbWrapper

def XbmcMetaFetcher(config, id):
    ''' Fetches meta data for movie identified with imdbid and saves it
    at location.
    '''
    i = imdbWrapper(config, http=True)
    m = i.findByImdbId(id, details = True)


def build_nfo(movie):
    root = XMLTree.Element("movie")

    root = add_sub(root, "title", movie.get("title"))
    root = add_sub(root, "id", movie.movieID)
    root = add_sub(root, "year", movie.get("year"))
    root = add_sub(root, "releasedate", get_release_date(movie.get('release dates')))
    root = add_sub(root, "top250", movie.get("top 250 rank"))
    root = add_sub(root, "rating", movie.get("rating"))
    root = add_sub(root, "votes", movie.get("votes"))
    root = add_sub(root, "mpaa", movie.get("mpaa"))
    root = add_sub(root, "certification", get_usa_certification(movie.get("certification")))
    root = add_sub(root, "genre", " / ".join(movie.get("genre")))
    root = add_sub(root, "studio", movie.get("production company")[0].get("name"))
    root = add_sub(root, "director", movie.get("director")[0].get("name"))
    root = add_sub(root, "credits", get_writers(movie.get("writer")))
    root = add_sub(root, "tagline", movie.get("tagline")[0])
    root = add_sub(root, "outline", movie.get("plot outline"))
    root = add_sub(root, "plot", movie.get('plot')[0].split("::")[0])
    root = add_sub(root, "runtime", "%s minutes" % movie.get("runtime")[0])


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = XMLTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding='utf-8')

def add_sub(elem, tag, text):
    if text:
        e = XMLTree.SubElement(elem, tag)
        e.text = text
        return elem
    else:
        return elem

def get_writers(writer_list):
    try:
        return " / ".join([x['name'] for x in writer_list])
    except:
        return None

def get_usa_certification(cert_list):
    for cert in cert_list:
        if 'usa' in cert.lower():
            return cert

    return None

def parse_imdb_date(date):
    ''' Takes an IMDB release date string ('USA::17 October 1999 (Hollywood, CA) (premeire)')
        and returns a datetime object.
    '''
    date_string = date.split(":")[2].split("(")[0].strip()
    try:
        date = datetime.datetime.strptime(date_string, "%d %B %Y")
    except:
        try:
            date = datetime.datetime.strptime(date_string, "%B %Y")
        except:
            try:
                date = datetime.datetime.strptime(date_string, "%Y")
            except:
                date = date_string

    return date

def get_release_date(date_list):
    if not date_list:
        return None
    date_string = False
    for date in date_list:
        if "(premiere)" in date:
            date_string = date
            break
    if date_string:
        date = parse_imdb_date(date_string)
        return "%s/%s/%s" % (date.month, date.day, date.year)
    else:
        return None

