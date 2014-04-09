from setuptools import setup
import py2app

plist = dict(
    CFBundleIdentifier="net.sabi.TransferDictationService",
    CFBundleName="Transfer Dictation",
    LSBackgroundOnly=1,
    NSServices=[
        dict(
            NSMenuItem=dict(
                default="Transfer Dictation",
            ),
            NSMessage="transferDictation",
            NSPortName="Transfer Dictation",
            NSRequiredContext=dict(
                NSServiceCategory="public.text"
            ),
            NSReturnTypes=[
                "NSStringPboardType",
            ],
            # NSSendTypes=[
            #     "NSStringPboardType",
            # ],
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
