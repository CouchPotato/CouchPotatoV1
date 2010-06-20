class rssFeed:

    def gettextelements(self, xml, path):
        ''' Find elements and return tree'''

        textelements = []
        try:
            elements = xml.findall(path)
        except:
            return
        for element in elements:
            textelements.append(element.text)
        return textelements

    def gettextelement(self, xml, path):
        ''' Find element and return text'''

        textelements = []
        try:
            return xml.find(path).text
        except:
            return

    class feedItem(dict):
        ''' NZB item '''
        
        def __getattr__(self, attr):
            return self.get(attr, None)
        
        __setattr__ = dict.__setitem__
        __delattr__ = dict.__delitem__



class infoProvider(rssFeed):

    type = 'infoProvider'
