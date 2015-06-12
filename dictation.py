#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import rpyc
import subprocess

__all__ = ('service', 'switch_to_app', 'show_app', 'start_in_foreground')

class _Service(object):
    __slots__ = ('connection', 'nesting_level')

    def __init__(self):
        self.connection = None
        self.nesting_level = 0

    def __enter__(self):
        if self.connection is None:
            self.connection = rpyc.connect('shirley7.local', 9999)
        try:
            self.connection.ping(timeout=1)
        except:
            self.close()
            raise Exception("Can't connect to dictation server (blocked?)")
        self.nesting_level += 1

        return self.connection.root

    def close(self):
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
        if appswitch('-hi', bundle_identifier):
            return appswitch('-si', bundle_identifier)
    return False

def start_in_foreground():
    switch_to_app()

    with service as s:
        s.set_mic_state('on')
        s.activate_word()

if __name__ == '__main__':
    start_in_foreground()
