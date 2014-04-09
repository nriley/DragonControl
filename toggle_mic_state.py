#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import dictation
import subprocess

if __name__ == '__main__':
	with dictation.service as s:
		initial_mic_state = s.get_mic_state()

		if initial_mic_state != 'on':
			s.set_mic_state('on')
			s.activate_word()
			message = 'Dragon is listening.'
			subprocess.call(['/usr/local/bin/appswitch', '-hi', 'com.vmware.fusion'])
			subprocess.call(['/usr/local/bin/appswitch', '-si', 'com.vmware.fusion'])
		else:
			s.set_mic_state('off')
			message = 'Dragon is not listening.'

		subprocess.call(['/usr/local/bin/growlnotify',
			'-t', 'Dragon Medical',
			'-m', message,
			'-d', 'mic state',
			'-I', '/Volumes/Shirley/Users/nicholas/Applications/Dragon Dictate.app'])
