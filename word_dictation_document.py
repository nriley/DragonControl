#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import dictation
import sys

__all__ = ['get_contents', 'set_contents', 'clear_contents']

def get_contents():
    with dictation.service as s:
        return s.get_word_document_contents().rstrip()

def set_contents(contents):
    with dictation.service as s:
        s.set_word_document_contents(contents.strip())

def clear_contents():
    set_contents('')

def get():
    sys.stdout.write(get_contents().encode('utf-8'))

def set():
    set_contents(sys.stdin.read())

def edit():
    with dictation.service as s:
        s.set_mic_state('on')
        s.activate_word()
        set()

def usage():
    print >> sys.stderr, 'usage:', sys.argv[0], '[get|set|edit]'
    sys.exit(1)

if __name__ == '__main__':
    try:
        if len(sys.argv) == 1:
            get()
        elif len(sys.argv) == 2:
            command = sys.argv[1]
            if command == 'get':
                get()
            elif command == 'set':
                set()
            elif command == 'edit':
                edit()
            else:
                usage()
        else:
            usage()
    except Exception as e:
        print >> sys.stderr, e
