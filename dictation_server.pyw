import ctypes
from ctypes import wintypes
import natlink
import os
import rpyc
import subprocess
import sys
import win32api
import win32con
import win32com.client
from win32com.client import constants
import win32gui
import _winreg

def Word():
    return win32com.client.gencache.EnsureDispatch('Word.Application')

def fix_addin():
    # Sometimes Word disables the addin, so it is impossible to
    # dictate into Word.  This is likely a bug in the addin, but I
    # don't have a choice but to work around it.
    with _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                         r'Software\Microsoft\Office\Word\Addins',
                         0, _winreg.KEY_ALL_ACCESS) as addins_key:
        try:
            _winreg.DeleteValue(addins_key, 'Dragon.Word2000Support.1')
        except WindowsError:
            pass

def wake_display():
    win32api.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SYSCOMMAND,
                         win32con.SC_MONITORPOWER, -1)

class APPBARDATA(ctypes.Structure):
    _fields_ = [('cbSize', wintypes.DWORD),
                ('hWnd', wintypes.HANDLE),
                ('uCallbackMessage', wintypes.UINT),
                ('uEdge', wintypes.UINT),
                ('rc', wintypes.RECT),
                ('lParam', wintypes.LPARAM)]

    def __repr__(self):
        return '<APPBARDATA: cbSize %d hWnd %d lParam %d>' % (
            self.cbSize, self.hWnd, self.lParam)

ABM_SETSTATE = 0xa

def set_taskbar_autohide(on):
    appbarData = APPBARDATA(
            cbSize=ctypes.sizeof(APPBARDATA),
            hWnd=win32gui.FindWindow('Shell_TrayWnd', ''),
            uCallbackMessage=0,
            uEdge=0,
            rc=wintypes.RECT(0, 0, 0, 0),
            lParam=1 if on else 0)
    ctypes.windll.shell32.SHAppBarMessage(ABM_SETSTATE, ctypes.byref(appbarData))

class DragonService(rpyc.Service):
    should_keep_serving = True

    def on_connect(self):
        natlink.natConnect(True)

    def on_disconnect(self):
        natlink.natDisconnect()

    def exposed_get_mic_state(self):
        return natlink.getMicState()

    def exposed_set_mic_state(self, state):
        try:
            natlink.setMicState(state)
        except natlink.NatError:
            if state != 'on':
                raise
            # An error is expected if using a remote microphone, as it can't be
            # enabled from the server side:
            # NatError: A SRERR_VALUEOUTOFRANGE error occurred calling
            # IDgnSREngineControl::SetMicState from DragCode.cpp 2249.
        wake_display()

    def exposed_activate_word(self):
        shell = win32com.client.Dispatch("WScript.Shell")
        if not shell.AppActivate('Word') or shell.AppActivate(' - Word'):
            fix_addin()
        word = Word()
        # if not word.Visible:
        #     # work around Word bug where it mismeasures screen dimensions
        #     # if the taskbar is set to autohide
        #     set_taskbar_autohide(False)
        #     set_taskbar_autohide(True)
        word.Visible = True
        documents = word.Documents
        if len(documents) == 0:
            documents.Add()
        wake_display()

    def exposed_get_word_document_contents(self):
        document = Word().Documents[0]
        document.Select()
        return document.Content.Text.replace('\r\n', '\n').replace('\r', '\n')

    def exposed_set_word_document_contents(self, contents):
        word = Word()
        word.ScreenUpdating = False
        word.Documents[0].Content.Text = contents
        word.Selection.GoTo(-1, 0, 0, r'\EndOfDoc')
        word.ScreenUpdating = True

    def exposed_stop_server(self):
        DragonService.should_keep_serving = False

def startNatSpeak():
    import natlinkstatus
    status = natlinkstatus.NatlinkStatus()
    natspeak_exe_path = os.path.join(
        status.getDNSInstallDir(), 'Program', 'natspeak.exe')
    os.startfile(natspeak_exe_path)

    import time
    while not natlink.isNatSpeakRunning():
        time.sleep(1)

class MicrophoneStateMonitor(object):
    __slots__ = ('monitor',)

    SCRIPT_PATH = 'microphone_state_monitor.pyw'

    def __enter__(self):
        devnull = open(os.devnull, 'wb')
        self.monitor = subprocess.Popen([sys.executable,
                                         self.SCRIPT_PATH],
                                         stdin=subprocess.PIPE,
                                         stdout=devnull, stderr=devnull)

    def __exit__(self, *exc_info):
        self.monitor.terminate()
        self.monitor = None
        subprocess.call([sys.executable, self.SCRIPT_PATH, 'stop'])

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # check that DNS is running; if we use natConnect() without a UI,
    # it starts DNS in a captive mode, without systemwide speech recognition
    if not natlink.isNatSpeakRunning():
        startNatSpeak()

    import logging
    logging.basicConfig(filename='dictation_server.log',
        format='%(asctime)s %(levelname)-5s %(name)s: %(message)s',
        datefmt='%m/%d %H:%M:%S',
        level=logging.DEBUG)

    with MicrophoneStateMonitor():
        from rpyc.utils.server import OneShotServer
        while DragonService.should_keep_serving:
            OneShotServer(DragonService, port=9999).start()

        # quit Word - try to clear resource leaks
        Word().Application.Quit(SaveChanges=constants.wdDoNotSaveChanges)
