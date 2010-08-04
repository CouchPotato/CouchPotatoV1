import xml.etree.ElementTree as XMLTree

class Rss:

    def getTextElements(self, xml, path):
        ''' Find elements and return tree'''

        textElements = []
        try:
            elements = xml.findall(path)
        except:
            return
        for element in elements:
            textElements.append(element.text)
        return textElements

    def getTextElement(self, xml, path):
        ''' Find element and return text'''

        try:
            return xml.find(path).text
        except:
            return

    def getItems(self, xml, path = 'channel/item'):
        return XMLTree.parse(xml).findall(path)

    class feedItem(dict):
        def __getattr__(self, attr):
            return self.get(attr, None)

        __setattr__ = dict.__setitem__
        __delattr__ = dict.__delitem__
