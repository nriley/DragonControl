#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import os
import socket
import subprocess
import sys
import time

__all__ = ('vmrun',)

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

def notify(message):
	subprocess.check_output(('osascript',
		(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Notify.scpt')),
		'Starting dictation', message))

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

def ensure_rdp():
	# start or unpause VM if needed
	vmx_paths = vmrun('list')
	if any(vmx_path.startswith(VM_PATH) for vmx_path in vmx_paths):
	    vmrun('unpause') # no way I know of to check if the VM is paused
	else:
		notify('Starting virtual machine')
		vmrun('start', 'nogui')

	# wait until the network is available
	while not output('/usr/sbin/scutil', '-r', VM_HOSTNAME).startswith('Reachable'):
	 	time.sleep(0.2)
		notify('Waiting for network')

	# wait until RDP is available
	while True:
		try:
			socket.create_connection((VM_HOSTNAME, 3389), 1)
			break
		except socket.error:
			notify('Waiting for RDP')

if __name__ == '__main__':
	ensure_rdp()
