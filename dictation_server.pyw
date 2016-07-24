import ctypes
from ctypes import wintypes
import natlink
import os
import rpyc
import struct
import subprocess
import sys
import win32api
import win32clipboard
import win32con
import win32com.client
from win32com.client import constants
import win32gui
import _winreg

# timing (http://stackoverflow.com/a/30024601/6372)
from contextlib import contextmanager
from timeit import default_timer

@contextmanager
def elapsed_timer():
    start = default_timer()
    elapsed = lambda: default_timer() - start
    yield lambda: elapsed()
    end = default_timer()
    elapsed = lambda: end - start

def Word():
    return win32com.client.gencache.EnsureDispatch('Word.Application')

def fix_addin():
    # Sometimes Word disables the addin, so it is impossible to
    # dictate into Word.  This is likely a bug in the addin, but I
    # don't have a choice but to work around it.
    addin_name = 'Dragon.Word2000Support.1'
    with _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                         r'Software\Microsoft\Office\Word\Addins',
                         0, _winreg.KEY_ALL_ACCESS) as addins_key:
        try:
            _winreg.DeleteKey(addins_key, addin_name)
            logging.info('Rescued Word addin from being disabled')
        except WindowsError:
            pass
    # Another location (http://superuser.com/questions/17557/)
    try:
        with _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Office\15.0\Word' +
                             r'\Resiliency\DisabledItems',
                             0, _winreg.KEY_ALL_ACCESS) as disabled_key:
            index = 0
            while True:
                name, data, rtype = _winreg.EnumValue(disabled_key, index)
                format = '3I'
                _, dll_len, name_len = struct.unpack_from(format, buffer(data))
                format += '%ds%ds' % (dll_len, name_len)
                _, _, _, dll_path, dll_name = struct.unpack(format, data)
                dll_path = dll_path.decode('utf16').rstrip('\0')
                dll_name = dll_name.decode('utf16').rstrip('\0')
                if dll_name.lower() == addin_name.lower():
                    _winreg.DeleteValue(disabled_key, name)
                    logging.info('Rescued Word addin from Resiliency')
                    break
                index += 1
    except WindowsError:
        pass

def get_document_text(document):
    return document.Content.Text.replace('\r\n', '\n').replace('\r', '\n').rstrip()

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

CLIPBOARD_RTF = win32clipboard.RegisterClipboardFormat('Rich Text Format')

class DragonService(rpyc.Service):
    __slots__ = ('natlink_connected',)

    should_keep_serving = True

    def on_connect(self):
        self.natlink_connected = False

    def on_disconnect(self):
        if self.natlink_connected:
            natlink.natDisconnect()

    def natlink(self):
        if not self.natlink_connected:
            with elapsed_timer() as elapsed:
                natlink.natConnect(True) # 0.006 - 4.5s
            logging.info('connected in %f', elapsed())
            self.natlink_connected = True
        return natlink

    def exposed_get_mic_state(self):
        return self.natlink().getMicState() # 0.006s

    def exposed_set_mic_state(self, state):
        try:
            self.natlink().setMicState(state) # 0.001 - 0.2s
        except natlink.NatError:
            if state != 'on':
                raise
            # An error is expected if using a remote microphone, as it can't be
            # enabled from the server side:
            # NatError: A SRERR_VALUEOUTOFRANGE error occurred calling
            # IDgnSREngineControl::SetMicState from DragCode.cpp 2249.
        if state == 'on':
            wake_display() # 0.3 - 0.4s

    def exposed_toggle_mic_state(self):
        state = 'on' if self.natlink().getMicState() == 'off' else 'off'
        try:
            self.natlink().setMicState(state)
        except natlink.NatError: # see explanation above
            if state != 'on':
                raise
        return state

    def exposed_activate_word(self):
        shell = win32com.client.Dispatch("WScript.Shell")
        if not (shell.AppActivate('Word') or shell.AppActivate(' - Word')):
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
        autohotkey.run('Activate Word')

        wake_display()

    def exposed_get_word_document_text(self):
        document = Word().ActiveDocument
        document.Select()
        return get_document_text(document)

    def exposed_set_word_document_text(self, text):
        word = Word()
        word.ScreenUpdating = False
        content = word.ActiveDocument.Content
        content.Delete()
        content.Text = text
        word.Selection.GoTo(-1, 0, 0, r'\EndOfDoc')
        word.ScreenUpdating = True

    def exposed_get_word_document_rtf(self, or_text_if_monostyled=False):
        word = Word()
        document = word.ActiveDocument
        document.Select()
        end = word.Selection.End
        if end == 0:
            return None
        if or_text_if_monostyled:
            # Convert to XML and check for run or paragraph properties.
            # If present, text is likely styled.
            # (Yes, I know parsing XML like this is quite brittle.)
            xml = word.Selection.XML
            body_index = xml.index('<w:body>')
            if (xml.find('<w:rPr>', body_index) == -1 and
                xml.find('<w:pPr>', body_index) == -1):
                return get_document_text(document)
        word.Selection.MoveEnd(Count=-1)
        word.Selection.Copy()
        win32clipboard.OpenClipboard()
        try:
            return win32clipboard.GetClipboardData(CLIPBOARD_RTF)
        finally:
            win32clipboard.CloseClipboard()

    def exposed_set_word_document_rtf(self, rtf):
        word = Word()
        word.ActiveDocument.Content.Delete()
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(CLIPBOARD_RTF, rtf)
        finally:
            win32clipboard.CloseClipboard()
        word.Selection.Paste()

    def exposed_stop_server(self):
        DragonService.should_keep_serving = False

def startNatSpeak():
    import natlinkstatus
    status = natlinkstatus.NatlinkStatus()
    natspeak_exe_path = os.path.join(
        status.getDNSInstallDir(), 'Program', 'natspeak.exe')
    win32api.ShellExecute(
        0, None, natspeak_exe_path,
        '/user "https://sabi.net/dragon/Nicholas Riley (v12)"', '', 0)

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

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    import autohotkey

    # check that DNS is running; if we use natConnect() without a UI,
    # it starts DNS in a captive mode, without systemwide speech recognition
    if not natlink.isNatSpeakRunning():
        startNatSpeak()

    import logging
    logging.basicConfig(filename='dictation_server.log',
        format='%(asctime)s.%(msecs)03d %(levelname)-5s %(name)s: %(message)s',
        datefmt='%m/%d %H:%M:%S',
        level=logging.DEBUG)

    sys.excepthook = handle_exception

    with MicrophoneStateMonitor():
        from rpyc.utils.server import OneShotServer
        while DragonService.should_keep_serving:
            OneShotServer(DragonService, port=9999).start()

        # quit Word - try to clear resource leaks
        Word().Application.Quit(SaveChanges=constants.wdDoNotSaveChanges)
