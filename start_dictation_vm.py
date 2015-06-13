#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import os
import socket
import subprocess
import sys
import time

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

def output(*args):
	return subprocess.check_output(args).rstrip('\n')

def notify(message):
	subprocess.check_output(('osascript',
		(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Notify.scpt')),
		'Starting dictation', message))

VMRUN_PATH = None
def vmrun(*args):
	global VMRUN_PATH
	if VMRUN_PATH is None:
		VMRUN_PATH = os.path.join(
			output('/usr/local/bin/launch', '-ni', 'com.vmware.fusion'),
				   'Contents', 'Library', 'vmrun')
	return output(VMRUN_PATH, *args)

# vmrun hangs otherwise: https://github.com/mitchellh/vagrant/issues/3426
# (my umask is typically 077)
os.umask(022)

# start VM if needed
vm_path = dictation_vm_path()
vmx_paths = vmrun('list').split('\n')[1:]
if not any(vmx_path.startswith(vm_path) for vmx_path in vmx_paths):
	notify('Starting virtual machine')
	vmrun('start', dictation_vm_path(), 'nogui')

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
