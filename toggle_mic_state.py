#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import rpyc
import subprocess

if __name__ == '__main__':
	c = rpyc.connect('shirley7', 9999)
	initial_mic_state = c.root.get_mic_state()

	if initial_mic_state != 'on':
		c.root.set_mic_state('on')
		message = 'Dragon is listening.'
		subprocess.call(['/usr/local/bin/appswitch', '-hi', 'com.vmware.fusion'])
		subprocess.call(['/usr/local/bin/appswitch', '-si', 'com.vmware.fusion'])
	else:
		c.root.set_mic_state('off')
		message = 'Dragon is not listening.'

	subprocess.call(['/usr/local/bin/growlnotify',
		'-t', 'Dragon Medical',
		'-m', message,
		'-d', 'mic state',
		'-I', '/Volumes/Shirley/Users/nicholas/Applications/Dragon Dictate.app'])
