#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import os
import socket
import subprocess
import sys
import time

__all__ = ('osascript', 'vmrun', 'wait_for_rdp')

HOME = os.path.expanduser('~')

# XXX change this if your virtual machine is somewhere else
VM_PATHS = (
	os.path.join(
		HOME, 'Documents', 'Virtual Machines.localized',
		'Windows 7.vmwarevm'),
	os.path.join(
		HOME, 'Library', 'Application Support',
		'VMware Fusion', 'Virtual Machines', 'Boot Camp',
		'Boot Camp.vmwarevm'))

# XXX duplicated
VM_HOSTNAME = 'shirley7.local'

def dictation_vm_path():
	for vm_path in VM_PATHS:
		if os.path.exists(vm_path):
			return vm_path

	print >> sys.stderr, 'Dictation VM not found at any of these locations:'
	for vm_path in VM_PATHS:
		print >> sys.stderr, '\t' + vm_path
	os.exit(1)
VM_PATH = dictation_vm_path()

def output(*args):
	return subprocess.check_output(args).rstrip('\n')

def osascript(script, *args):
	return subprocess.check_output(['/usr/bin/osascript',
		os.path.join(os.path.dirname(os.path.abspath(__file__)),
				     script + '.scpt')] + list(args))

def notify(message):
	osascript('Notify', 'Dictation', message)

class WaitNotifier(object):
	__slots__ = ('message', 'start_time', 'wait_seconds')

	def __init__(self, message, wait_seconds=2):
		self.message = message
		self.wait_seconds = wait_seconds

	def __enter__(self):
		self.start_time = time.time()
		return self

	def __call__(self):
		wait_time = self.wait_seconds - (time.time() - self.start_time)
		notify(self.message)
		if wait_time > 0:
			time.sleep(wait_time)
		self.start_time = time.time()

	def __exit__(self, *exc_info):
		pass

VMRUN_PATH = os.path.join(
	output('/usr/local/bin/launch', '-ni', 'com.vmware.fusion'),
		   'Contents', 'Library', 'vmrun')
def vmrun(*args):
	# vmrun hangs otherwise: https://github.com/mitchellh/vagrant/issues/3426
	# (my umask is typically 077)
	os.umask(022)
	if args[0] == 'list':
		return output(VMRUN_PATH, args[0]).split('\n')[1:]
	return output(VMRUN_PATH, args[0], VM_PATH, *args[1:])

def wait_for_rdp():
	# wait until the network is available
	with WaitNotifier('Waiting for network') as wait_notify:
		while not output('/usr/sbin/scutil', '-r', VM_HOSTNAME).startswith('Reachable'):
			wait_notify()

	# wait until RDP is available
	with WaitNotifier('Waiting for RDP') as wait_notify:
		while True:
			try:
				socket.create_connection((VM_HOSTNAME, 3389), 1)
				break
			except socket.error:
				wait_notify()

def start():
	# start or unpause VM if needed
	vmx_paths = vmrun('list')
	if any(vmx_path.startswith(VM_PATH) for vmx_path in vmx_paths):
	    vmrun('unpause') # no way I know of to check if the VM is paused
	else:
		notify('Starting virtual machine')
		vmrun('start', 'nogui')

if __name__ == '__main__':
    start()
    wait_for_rdp()
