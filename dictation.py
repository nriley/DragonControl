#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import rpyc
import subprocess
import vm

__all__ = ('service', 'switch_to_app', 'show_app', 'start_in_foreground')

class _Service(object):
    __slots__ = ('connection', 'nesting_level', 'ip_address')

    def __init__(self):
        self.connection = None
        self.ip_address = None
        self.nesting_level = 0

    def __enter__(self):
        if self.ip_address is None:
            self.ip_address = vm.guest_ip_address()
            if self.ip_address is None:
                raise Exception("Dictation server VM not ready")
        try:
            if self.connection is None:
                self.connection = rpyc.connect(self.ip_address, 9999)
            self.connection.ping(timeout=1)
        except:
            self.close()
            if vm.guest_ip_address(use_cached=False) != self.ip_address:
                # Transfer Dictation can stick around through server restarts
                # should repeat at most once
                self.ip_address = None
                return self.__enter__()
            else:
                raise Exception(
                    "Can't connect to dictation server (blocked?): " +
                    __import__('traceback').format_exc())
        self.nesting_level += 1

        return self.connection.root

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def __exit__(self, *exc_info):
        self.nesting_level -= 1
        if self.nesting_level == 0:
            self.close()

service = _Service()

def appswitch(*args):
    return subprocess.call(['/usr/local/bin/appswitch'] + list(args)) == 0

DICTATION_APPS = ('com.p5sys.jump.mac.viewer', 'com.vmware.fusion')

def switch_to_app():
    return any(appswitch('-i', bundle_identifier)
               for bundle_identifier in DICTATION_APPS)

def show_app():
    for bundle_identifier in DICTATION_APPS:
        if appswitch('-Pi', bundle_identifier):
            return appswitch('-si', bundle_identifier)
    return False

def start_in_foreground():
    switch_to_app()

    with service as s:
        s.set_mic_state('on')
        s.activate_word()

if __name__ == '__main__':
    start_in_foreground()
