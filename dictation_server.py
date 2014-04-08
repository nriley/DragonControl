import natlink
import rpyc
import sys
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

if __name__ == '__main__':
    from rpyc.utils.server import OneShotServer
    while True:
        OneShotServer(DragonService, port=9999).start()
