#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import rpyc

if __name__ == '__main__':
	c = rpyc.connect('shirley7', 9999)
	initial_mic_state = c.root.get_mic_state()

	if initial_mic_state != 'on':
		c.root.set_mic_state('on')
		message = 'Dragon is listening'
	else:
		c.root.set_mic_state('off')
		message = 'Dragon is not listening'

	import subprocess
	subprocess.call(['/usr/local/bin/growlnotify',
		'-t', 'Dragon Medical',
		'-m', message,
		'-d', 'mic state',
		'-I', '/Volumes/Shirley/Users/nicholas/Applications/Dragon Dictate.app'])
