#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import dictation
import subprocess

if __name__ == '__main__':
	with dictation.service as s:
		initial_mic_state = s.get_mic_state()

		if initial_mic_state != 'on':
			s.set_mic_state('on')
			s.activate_word()
			dictation.show_app()
		else:
			s.set_mic_state('off')
			message = 'Dragon is not listening.'
