from imdb import IMDb

def getnfo(imdb_id = False, tmdb_id = False):
    ''' Fetches all the available information for the specified id
        and returns a dict.  Each key corresponds to a tag name as
        specfied
    '''