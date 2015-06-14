#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import dictation, socket, vm

if __name__ == '__main__':
	try:
		with dictation.service as s:
			s.stop_server()
	except socket.error:
		pass # server isn't running
	vm.notify('Restarting virtual machine')
	vm.vmrun('reset')
	vm.wait_for_rdp()
	# this is duplicative, but should be idempotent
	vm.osascript('Start Dictation via RDP')
