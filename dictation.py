#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import rpyc
import subprocess

class _Service(object):
    __slots__ = ('connection', 'nesting_level')

    def __init__(self):
        self.connection = None
        self.nesting_level = 0

    def __enter__(self):
        if self.connection is None:
            self.connection = rpyc.connect('shirley7', 9999)
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

def start_in_foreground():
    subprocess.call(['/usr/local/bin/appswitch', '-i', 'com.vmware.fusion'])
    with service as s:
        s.set_mic_state('on')
        s.activate_word()

if __name__ == '__main__':
    start_in_foreground()
