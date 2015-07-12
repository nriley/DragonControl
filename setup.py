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
