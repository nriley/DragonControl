# NOTE: At least in 10.11.0-10.11.2 the built-in py2app won't build
# with SIP on (default).

# *** creating application bundle: Transfer Dictation ***
# error: [Errno 1] Operation not permitted: '/Users/nicholas/Documents/Development/DragonControl/dist/Transfer Dictation.service/Contents/MacOS/Transfer Dictation'

# You can build/install your own py2app in the virtualenv to get
# around this.

# See <http://stackoverflow.com/a/34374232/6372>.

from setuptools import setup
import py2app

plist = dict(
    CFBundleIdentifier="net.sabi.TransferDictationService",
    CFBundleName="Transfer Dictation",
    CFBundleVersion="1.0.0",
    LSBackgroundOnly=1,
    NSServices=[
        dict(
            NSMenuItem=dict(
                default="Receive Dictation",
            ),
            NSMessage="receiveDictation",
            NSPortName="Transfer Dictation",
            NSRequiredContext=dict(
                NSServiceCategory="public.text"
            ),
            NSReturnTypes=[
                "public.rtf",
                "public.utf8-plain-text",
            ],
        ),
        dict(
            NSMenuItem=dict(
                default="Send Dictation",
            ),
            NSMessage="sendDictation",
            NSPortName="Transfer Dictation",
            NSRequiredContext=dict(
                NSServiceCategory="public.text"
            ),
            NSSendTypes=[
                "public.rtf",
                "public.utf8-plain-text",
            ],
        ),
    ],
)

setup(
    name="Transfer Dictation",
    app=["transfer_dictation.py"],
    options=dict(
        py2app=dict(
            extension=".service",
            plist=plist
        )
    )
)
