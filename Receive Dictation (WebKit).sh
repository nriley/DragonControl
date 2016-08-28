#!/bin/zsh -f

/usr/bin/osascript \
	-e 'tell application "System Events"' \
	-e 'ignoring application responses' \
	-e 'click menu item "Receive Dictation" of menu of menu item "Services" of menu 2 of menu bar 1 of (first process whose frontmost is true)' \
	-e 'end ignoring' \
	-e 'end tell'
