#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import rpyc
import sys

if __name__ == '__main__':
	try:
		c = rpyc.connect('shirley7', 9999)
		sys.stdout.write(c.root.get_word_document_contents().encode('utf-8').strip())
	except Exception as e:
		print >> sys.stderr, e
