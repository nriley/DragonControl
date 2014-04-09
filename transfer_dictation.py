import Cocoa
import objc
from PyObjCTools import AppHelper
from get_word_document_contents import get_word_document_contents

def serviceSelector(fn): return objc.selector(fn, signature=b"v@:@@o^@")

class TransferDictationService(Cocoa.NSObject):
    @serviceSelector
    def transferDictation_userData_error_(self, pboard, data, err):

        try:
        #     types = pboard.types()
        #     pboardString = None
        #     if Cocoa.NSStringPboardType in types:
        #         pboardString = pboard.stringForType_(Cocoa.NSStringPboardType)
        #     if pboardString is None:
        #         return ERROR(Cocoa.NSLocalizedString(
        #             "Error: Pasteboard doesn't contain a string.",
        #             "Pasteboard couldn't give string."
        #         ))
            newString = get_word_document_contents()
            if not newString:
                return u'There is no dictated text to transfer.'

            types = [Cocoa.NSStringPboardType]
            pboard.declareTypes_owner_([Cocoa.NSStringPboardType], None)
            pboard.setString_forType_(newString, Cocoa.NSStringPboardType)
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
