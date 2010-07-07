from string import ascii_letters, digits
import unicodedata

class rss:

    def toSaveString(self, string):
        string =  ''.join((c for c in unicodedata.normalize('NFD', unicode(string)) if unicodedata.category(c) != 'Mn'))
        safe_chars = ascii_letters + digits + '_ -.,'
        return ''.join([char if char in safe_chars else '' for char in string])

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