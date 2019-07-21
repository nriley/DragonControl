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
		'Windows 7.vmwarevm'))

VM_IP_CACHE_PATH = os.path.join(HOME, '.dragoncontrol_vm_ip')

def dictation_vm_path():
	for vm_path in VM_PATHS:
		if os.path.exists(vm_path):
			return os.path.realpath(vm_path)

	print >> sys.stderr, 'Dictation VM not found at any of these locations:'
	for vm_path in VM_PATHS:
		print >> sys.stderr, '\t' + vm_path
	os.exit(1)
VM_PATH = dictation_vm_path()

def output(*args):
	return subprocess.check_output(args).rstrip('\n')

def osascript(script, *args):
	script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
							   script + '.scpt')
	if not os.path.exists(script_path):
		print >> sys.stderr, "Script doesn't exist:", script, ' '.join(args)
		return False
	return subprocess.check_output(
		['/usr/bin/osascript', script_path] + list(args))

def notify(message):
	osascript('Notify', 'Dictation', message)

class WaitNotifier(object):
	__slots__ = ('message', 'start_time', 'wait_seconds',
				 'notify_time', 'notify_seconds')

	def __init__(self, message, wait_seconds=0.1):
		self.message = message
		self.wait_seconds = wait_seconds
		self.notify_seconds = max(wait_seconds, 4)

	def __enter__(self):
		self.start_time = time.time()
		self.notify_time = None
		return self

	@property
	def wait_seconds_remaining(self):
		return self.wait_seconds - (time.time() - self.start_time)

	@property
	def notify_seconds_remaining(self):
		if self.notify_time is None:
			return 0
		return self.notify_seconds - (time.time() - self.notify_time)

	def __call__(self):
		notify_seconds_remaining = self.notify_seconds_remaining
		wait_seconds_remaining = self.wait_seconds_remaining
		if notify_seconds_remaining < wait_seconds_remaining:
			if notify_seconds_remaining > 0:
				time.sleep(notify_seconds_remaining)
			notify(self.message)
			self.notify_time = time.time()
			wait_seconds_remaining = self.wait_seconds_remaining
		if wait_seconds_remaining > 0:
			time.sleep(wait_seconds_remaining)
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
	ip_address = guest_ip_address(use_cached=False)

	# wait until RDP is available
	with WaitNotifier('Waiting for RDP') as wait_notify:
		while True:
			try:
				socket.create_connection((ip_address, 3389), 1)
				break
			except socket.error:
				wait_notify()

def update_jump(jump_connection_path):
	ip_address = guest_ip_address() or guest_ip_address(use_cached=False)

	import json
	jump_connection = json.load(file(jump_connection_path, 'rb'))
	jump_connection['TcpHostName'] = ip_address
	json.dump(jump_connection, file(jump_connection_path, 'wb'), indent=2)

def start():
	# start or unpause VM if needed
	vmx_paths = vmrun('list')
	if any(vmx_path.startswith(VM_PATH) for vmx_path in vmx_paths):
		vmrun('unpause')  # no way I know of to check if the VM is paused
	else:
		notify('Starting virtual machine')
		vmrun('start', 'nogui')

def pause():
	vmrun('pause')
	notify('Virtual machine paused')

def unpause():
	vmrun('unpause')
	notify('Virtual machine unpaused')

def guest_ip_address(use_cached=True):
	if use_cached:
		try:
			return file(VM_IP_CACHE_PATH, 'r').read()
		except IOError:
			pass
	vmrun_cmd = [VMRUN_PATH, 'getGuestIPAddress', VM_PATH, '-wait']
	vmrun_process = subprocess.Popen(vmrun_cmd, stdout=subprocess.PIPE)
	with WaitNotifier('Waiting for network') as wait_notify:
		while True:
			returncode = vmrun_process.poll()
			if returncode == 0:
				address = vmrun_process.stdout.read().rstrip()
				if address != 'unknown':
					file(VM_IP_CACHE_PATH, 'w').write(address)
					return address
			elif returncode is not None:  # VM likely not running
				if use_cached:
					break
				raise subprocess.CalledProcessError(returncode, vmrun_cmd,
													vmrun_process.stdout.read())
			wait_notify()
	try:
		os.unlink(VM_IP_CACHE_PATH)
	except OSError:
		pass

if __name__ == '__main__':
	if len(sys.argv) == 1:
		start()
		wait_for_rdp()
	elif sys.argv[1] == 'pause':
		pause()
	elif sys.argv[1] == 'unpause':
		unpause()
	elif sys.argv[1] == 'update_jump':
		update_jump(sys.argv[2])
	elif sys.argv[1] == 'guest_ip_address_cached':
		print guest_ip_address(use_cached=True)
	elif sys.argv[1] == 'guest_ip_address_uncached':
		print guest_ip_address(use_cached=False)
