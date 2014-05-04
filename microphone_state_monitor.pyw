import logging
import natlink
import subprocess
import win32gui
import win32process

def microphone_state_autohotkey(*args):
    subprocess.Popen((AHK_EXE, 'Dragon Microphone State.ahk') + args,
                     creationflags=win32process.CREATE_NEW_PROCESS_GROUP)

last_mic_state = None

def natlink_change(user_or_mic, changed_to):
    global last_mic_state
    if user_or_mic != 'mic':
        return
    if changed_to == 'sleeping': # makes comparison easier
        changed_to = 'off'
    if last_mic_state == changed_to:
        return # flapping between off/sleeping at startup can trigger a race
    last_mic_state = changed_to
    microphone_state_autohotkey(changed_to)

def destroy_window():
    microphone_state_autohotkey()

if __name__ == '__main__':
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    import sys
    should_start_monitor = len(sys.argv) == 1

    if should_start_monitor:
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

        if should_start_monitor:
            natlink.natConnect(True)
            logging.debug('getMicState at startup: ' + natlink.getMicState())
            natlink.setChangeCallback(natlink_change)
            win32gui.PumpMessages()
        else:
            destroy_window()
    except:
        logging.exception('')
