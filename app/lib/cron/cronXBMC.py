from app.lib.cron.cronBase import cronBase
from app.lib.provider.movie.sources.theMovieDb import theMovieDb

def XbmcMetaFetcher(config, id, location):
    ''' Fetches meta data for movie identified with imdbid and saves it
    at location.
    '''
    tmdb = theMovieDb(config)
    #tmdb_id = tmdb.findByImdbId(imdbid)['id']
    xml = tmdb.getXML(id).read()
    import pdb; pdb.set_trace()
    pass

