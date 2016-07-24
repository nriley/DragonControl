__all__ = ('run',)

import subprocess
import sys
import win32process

sys.path.append(r'..\Unimacro')
import autohotkeyactions
# GetAhkExe() doesn't return the location of the AHK EXE.
# Instead, ahk_is_active() does.  No, I have no idea either.
AHK_EXE = autohotkeyactions.ahk_is_active()

def run(script, *args):
    subprocess.Popen((AHK_EXE, script + '.ahk') + args,
                     creationflags=win32process.CREATE_NEW_PROCESS_GROUP)
