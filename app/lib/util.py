'''
Created on 31.07.2010

@author: Christian
'''
from app import latinToAscii
from string import ascii_letters, digits
import re
import unicodedata

def sanitize_search_string(string):
        string = latinToAscii(string)
        string = ''.join((c for c in unicodedata.normalize('NFD', unicode(string)) if unicodedata.category(c) != 'Mn'))
        safe_chars = ascii_letters + digits + ' \''
        r = ''.join([char if char in safe_chars else ' ' for char in string])
        return re.sub('\s+' , ' ', r).replace('\'s', 's').replace('\'', ' ')