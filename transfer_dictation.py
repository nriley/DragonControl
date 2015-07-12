# Testing service:
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
            newString = word_dictation_document.get_contents()
            if not newString:
                return u'There is no dictated text to transfer.'

            types = [Cocoa.NSPasteboardTypeString]
            pboard.declareTypes_owner_([Cocoa.NSPasteboardTypeString], None)
            pboard.setString_forType_(newString, Cocoa.NSPasteboardTypeString)
        except:
            import traceback
            Cocoa.NSLog(traceback.format_exc())

    @serviceSelector
    def sendDictation_userData_error_(self, pboard, data, err):
        try:
            types = pboard.types()
            if Cocoa.NSPasteboardTypeString not in types:
                return
            with dictation.service:
                dictation.start_in_foreground()
                oldString = pboard.stringForType_(Cocoa.NSPasteboardTypeString)
                word_dictation_document.set_contents(oldString)
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
