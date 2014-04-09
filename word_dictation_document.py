#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import dictation
import sys

def get_contents():
    with dictation.service as s:
        return s.get_word_document_contents().strip()

def set_contents(contents):
    with dictation.service as s:
        s.set_word_document_contents(contents.strip())

if __name__ == '__main__':
    try:
        sys.stdout.write(get_contents().encode('utf-8'))
    except Exception as e:
        print >> sys.stderr, e
