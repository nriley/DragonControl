#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import rpyc
import sys

def connection():
    return rpyc.connect('shirley7', 9999)

def get_contents():
    c = connection()
    return c.root.get_word_document_contents().strip()

def set_contents(contents):
    c = connection()
    c.root.set_word_document_contents(contents.strip())

if __name__ == '__main__':
    try:
        sys.stdout.write(get_contents().encode('utf-8'))
    except Exception as e:
        print >> sys.stderr, e
