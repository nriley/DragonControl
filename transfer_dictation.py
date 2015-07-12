# Testing service:
# ACTIVATE THE VIRTUALENV BEFORE DOING THIS OR THE SERVICE ALWAYS FAILS!
# killall 'Transfer Dictation'; python setup.py py2app && touch ~/Library/Services && open -a TextEdit

import Cocoa
import objc
import dictation
import word_dictation_document
from PyObjCTools import AppHelper

def serviceSelector(fn): return objc.selector(fn, signature=b"v@:@@o^@")

class TransferDictationService(Cocoa.NSObject):
    @serviceSelector
    def receiveDictation_userData_error_(self, pboard, data, err):
        try:
            pasteboard_type = Cocoa.NSPasteboardTypeString
            try:
                contents = word_dictation_document.get_rtf(
                    or_text_if_monostyled=True)
                if contents.startswith(r'{\rtf'):
                    pasteboard_type = Cocoa.NSPasteboardTypeRTF
            except:
                contents = word_dictation_document.get_text()
            if not contents:
                return u'There is no dictated text to transfer.'
            pboard.declareTypes_owner_([pasteboard_type], None)
            pboard.setString_forType_(contents, pasteboard_type)
        except:
            import traceback
            Cocoa.NSLog(traceback.format_exc())

    @serviceSelector
    def sendDictation_userData_error_(self, pboard, data, err):
        try:
            types = pboard.types()
            if Cocoa.NSPasteboardTypeRTF in types:
                pasteboard_type = Cocoa.NSPasteboardTypeRTF
                setter = word_dictation_document.set_rtf
            elif Cocoa.NSPasteboardTypeString in types:
                pasteboard_type = Cocoa.NSPasteboardTypeString
                setter = word_dictation_document.set_text
            else:
                return
            with dictation.service:
                dictation.start_in_foreground()
                setter(pboard.stringForType_(pasteboard_type))
        except:
            import traceback
            Cocoa.NSLog(traceback.format_exc())

if __name__ == '__main__':
    try:
        serviceProvider = TransferDictationService.alloc().init()
        Cocoa.NSRegisterServicesProvider(serviceProvider, u'TransferDictationService')
        AppHelper.runConsoleEventLoop()
    except:
        import traceback
        Cocoa.NSLog(traceback.format_exc())
