import natlink
import subprocess
import win32gui
import win32process

def autohotkey(script, *args):
    subprocess.Popen((AHK_EXE, script) + args,
        creationflags=win32process.CREATE_NEW_PROCESS_GROUP)

def natlink_change(user_or_mic, changed_to):
    if user_or_mic != 'mic':
        return
    autohotkey('Dragon Microphone State.ahk', changed_to)

if __name__ == '__main__':
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    import logging
    logging.basicConfig(filename='microphone_state_monitor.log',
        format='%(asctime)s %(levelname)-5s %(name)s: %(message)s',
        datefmt='%m/%d %H:%M:%S',
        level=logging.DEBUG)

    try:
        import sys
        sys.path.append(r'..\Unimacro')
        import autohotkeyactions
        # GetAhkExe() doesn't return the location of the AHK EXE.
        # Instead, ahk_is_active() does.  No, I have no idea either.
        AHK_EXE = autohotkeyactions.ahk_is_active()

        natlink.natConnect(True)
        natlink_change('mic', natlink.getMicState())
        natlink.setChangeCallback(natlink_change)
        win32gui.PumpMessages()
    except:
        logging.exception('')
