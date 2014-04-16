import natlink
import subprocess
import win32process
import win32gui

def autohotkey(script, *args):
    subprocess.Popen((AHK_EXE, script) + args,
        creationflags=win32process.CREATE_NEW_PROCESS_GROUP)

def natlink_change(user_or_mic, changed_to):
    if user_or_mic != 'mic':
        return
    autohotkey('Dragon Microphone State.ahk', changed_to)

if __name__ == '__main__':
    import sys
    sys.path.append(r'C:\NatLink\Unimacro')
    import autohotkeyactions
    # GetAhkExe() doesn't return the location of the AHK EXE.
    # Instead, ahk_is_active() does.  No, I have no idea either.
    AHK_EXE = autohotkeyactions.ahk_is_active()

    natlink.natConnect(True)
    natlink.setChangeCallback(natlink_change)
    win32gui.PumpMessages()
