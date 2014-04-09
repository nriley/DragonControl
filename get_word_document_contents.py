#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import rpyc
import sys

def get_word_document_contents():
    c = rpyc.connect('shirley7', 9999)
    return c.root.get_word_document_contents().encode('utf-8').strip()

if __name__ == '__main__':
    try:
        sys.stdout.write(get_word_document_contents())
    except Exception as e:
        print >> sys.stderr, e
