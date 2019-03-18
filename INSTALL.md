An incomplete guide.

### Install on Windows

- [Python 2.7](https://www.python.org/downloads/windows/) — needs to be x86, not x86-64
- [Natlink](https://qh.antenna.nl/unimacro/installation/installation.html) — in default location, `C:\NatLink`

Complete the NatLink installation and configure it as follows (assuming you don't want to use other features of NatLink):

- Disable NatLink (Vocola and Unimacro will automatically be disabled).

```
>pip install rpyc
```

Check out DragonControl to `C:\NatLink\DragonControl` on the Windows side.

Add a shortcut to `dictation_server.pyw` to your `Startup` directory.

Edit `dictation_server.pyw` to reflect your current Dragon user in `startNatSpeak`.

Exit Dragon.

Run `dictation_server.pyw` from the command line to make sure it works.

### Install on Mac

Check out DragonControl to `~/Documents/Development/DragonControl` on the Mac side.

```
% sudo -s
# umask 022
# python -m ensurepip
# pip install virtualenv
# ^D
% cd ~/Documents/Development/DragonControl
% virtualenv .
% source bin/activate
(DragonControl) % pip install py2app rpyc
(DragonControl) % python setup.py py2app -A
```

### Suggested script keyboard equivalents

|               Script              | Keyboard | Keypad |
| --------------------------------- | -------- | ------ |
| Dictation → Day One               | ⌃⌥J      |        |
| Dictation → Fantastical           | ⌃⌥I      |        |
| Dictation Clear                   | ⌃⌥C      | .      |
| Dictation Edit                    | ⌃⌥E      | –      |
| Dictation Lowercase First Word    | ⌃⌥F      | *      |
| Dictation Restart                 |          |        |
| Dictation Start in Foreground     | ⌃⌥[      |        |
| Dictation Start via RDP           | ⌃⌥D      |        |
| Dictation Stop                    |          |        |
| Dictation Toggle Microphone State | ⌃⌥`      | +      |
| Dictation VM Audio Reset          |          |        |
| Dictation VM Pause                | ⌃⌥P      |        |
| Dictation VM Unpause              | ⌃⌥U      |        |
