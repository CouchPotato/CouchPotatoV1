from app.lib.provider.nzb.sources.nzbs import nzbs

class nzbSearcher():
    
    sources = []
    
    def __init__(self, config):
        
        self.config = config
        
        #config nzbs
        s = nzbs(config)
        self.sources.append(s)
        
    
    def find(self, q):
        ''' Find movie by name '''
        
        for source in self.sources:
            result = source.find(q)
            if result:
                return result
            
        return []
        
        

    def findById(self, id):
        ''' Find movie by TheMovieDB ID '''
        
        for source in self.sources:
            result = source.findById(id)
            if result:
                return result
            
        return []
        
        

    def findByImdbId(self, id):
        ''' Find movie by IMDB ID '''
        
        for source in self.sources:
            result = source.findByImdbId(id)
            if result:
                return result
            
        return []
        
        