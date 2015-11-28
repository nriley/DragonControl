#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import dictation
import subprocess

if __name__ == '__main__':
	with dictation.service as s:
		mic_state = s.toggle_mic_state()

		if mic_state == 'on':
			s.activate_word()
			dictation.show_app()
