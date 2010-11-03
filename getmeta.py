from hachoir_parser import createParser
from hachoir_metadata import extractMetadata
from hachoir_core.cmd_line import unicodeFilename

import json
import sys


def getMetadata(filename):
    filename, realname = unicodeFilename(filename), filename
    parser = createParser(filename, realname)
    try:
        metadata = extractMetadata(parser)
    except:
        return None

    if metadata is not None:
        metadata = metadata.exportPlaintext()
        return metadata
    return None

def parseMetadata(meta):
    #find indexes of headings
    splits = []
    for i in xrange(len(meta)):
        if meta[i][:2] != '- ':
            splits.append(i)

    #use found indexes to split list of metadata
    sections = {}
    for i in xrange(len(splits)):
        section_name = meta[splits[i]].strip(":")
        try:
            section_contents = meta[splits[i]+1:splits[i+1]]
        except IndexError:
            section_contents = meta[splits[i]+1:]
        if section_name not in sections:
            sections[section_name] = [section_contents]
        else:
            sections[section_name].append(section_contents)

    for section in sections:
        streams = []
        for stream in sections[section]:
            streams.append(_parseKVList(stream))
        sections[section] = streams

    return sections

def _parseKVList(kvlist):
    parsed = {}
    for kv in kvlist:
        parsed[kv[2:kv.find(":")]] = kv[kv.find(":")+2:]
    return parsed

print json.dumps(parseMetadata(getMetadata(sys.argv[1])))