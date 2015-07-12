#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import dictation
import sys

__all__ = ['get_text', 'get_rtf', 'set_text', 'set_rtf', 'clear_contents']

def get_text():
    with dictation.service as s:
        return s.get_word_document_text()

def get_rtf():
    with dictation.service as s:
        return s.get_word_document_rtf()

def set_text(text):
    with dictation.service as s:
        s.set_word_document_text(text.strip())

def set_rtf(rtf):
    with dictation.service as s:
        return s.set_word_document_rtf(rtf.encode('ascii'))

def clear_contents():
    set_text('')

def get(format=None):
    if format and format.lower() == 'rtf':
        sys.stdout.write(get_rtf())
    else:
        sys.stdout.write(get_text().encode('utf-8'))

def set(format=None):
    contents = sys.stdin.read()
    if format and format.lower() == 'rtf':
        set_rtf(contents)
    else:
        set_text(contents)

def edit():
    with dictation.service as s:
        s.set_mic_state('on')
        s.activate_word()
        set()

def usage():
    print >> sys.stderr, 'usage:', sys.argv[0], '[get|set|edit] [text|RTF]'
    sys.exit(1)

if __name__ == '__main__':
    try:
        if len(sys.argv) == 1:
            get()
        elif len(sys.argv) > 3:
            usage()
        command = sys.argv[1]
        format = sys.argv[2] if len(sys.argv) == 3 else None
        if command == 'get':
            get(format)
        elif command == 'set':
            set(format)
        elif command == 'edit':
            edit()
        else:
            usage()
    except Exception as e:
        print >> sys.stderr, e
        sys.exit(1)
