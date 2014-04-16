import natlink
import rpyc
import win32com.client

def Word():
    return win32com.client.Dispatch('Word.Application')

class DragonService(rpyc.Service):
    def on_connect(self):
        natlink.natConnect(True)

    def on_disconnect(self):
        natlink.natDisconnect()

    def exposed_get_mic_state(self):
        return natlink.getMicState()

    def exposed_set_mic_state(self, state):
        natlink.setMicState(state)

    def exposed_activate_word(self):
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.AppActivate('Word')
        shell.AppActivate(' - Word')
        word = Word()
        word.Visible = True
        documents = word.Documents
        if len(documents) == 0:
            documents.Add()

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

def startNatSpeak():
    import natlinkstatus
    import os
    status = natlinkstatus.NatlinkStatus()
    natspeak_exe_path = os.path.join(
        status.getDNSInstallDir(), 'Program', 'natspeak.exe')
    os.startfile(natspeak_exe_path)

    import time
    while not natlink.isNatSpeakRunning():
        time.sleep(1)

if __name__ == '__main__':
    # check that DNS is running; if we use natConnect() without a UI,
    # it starts DNS in a captive mode, without systemwide speech recognition
    if not natlink.isNatSpeakRunning():
        startNatSpeak()

    from rpyc.utils.server import OneShotServer
    while True:
        OneShotServer(DragonService, port=9999).start()
