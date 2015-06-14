#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import dictation, vm

if __name__ == '__main__':
	with dictation.service as s:
		s.stop_server()
	vm.vmrun('reset')