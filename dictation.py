#!/Users/nicholas/Documents/Development/DragonControl/bin/python

import rpyc
import subprocess

def start_in_foreground():
    subprocess.call(['/usr/local/bin/appswitch', '-i', 'com.vmware.fusion'])
    c = rpyc.connect('shirley7', 9999)
    c.root.set_mic_state('on')
    c.root.activate_word()

if __name__ == '__main__':
    start_in_foreground()
