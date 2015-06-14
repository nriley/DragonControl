#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import dictation, socket, sys, vm

if __name__ == '__main__':
	try:
		with dictation.service as s:
			s.stop_server()
	except socket.error:
		pass # server isn't running
	if len(sys.argv) == 1:
		vm.notify('Shutting down virtual machine')
		vm.vmrun('stop')
