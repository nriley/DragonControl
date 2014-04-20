import natlink
import os
import rpyc
import win32api
import win32con
import win32com.client

def Word():
    return win32com.client.Dispatch('Word.Application')

def wake_display():
    win32api.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SYSCOMMAND,
                         win32con.SC_MONITORPOWER, -1)

class DragonService(rpyc.Service):
    should_keep_serving = True

    def on_connect(self):
        natlink.natConnect(True)

    def on_disconnect(self):
        natlink.natDisconnect()

    def exposed_get_mic_state(self):
        return natlink.getMicState()

    def exposed_set_mic_state(self, state):
        natlink.setMicState(state)
        wake_display()

    def exposed_activate_word(self):
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.AppActivate('Word')
        shell.AppActivate(' - Word')
        word = Word()
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

    def __enter__(self):
        import subprocess, sys

        devnull = open(os.devnull, 'wb')
        self.monitor = subprocess.Popen([sys.executable,
                                         'microphone_state_monitor.pyw'],
                                         stdin=subprocess.PIPE,
                                         stdout=devnull, stderr=devnull)

    def __exit__(self, *exc_info):
        self.monitor.terminate()
        self.monitor = None

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
