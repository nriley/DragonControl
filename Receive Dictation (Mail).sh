#!/bin/zsh

osascript -e 'tell application "System Events"' \
		  -e 'ignoring application responses' \
		  -e 'click menu item "Receive Dictation" of menu of menu item "Services" of menu "Mail" of menu bar 1 of process "Mail"' \
		  -e 'end ignoring' \
		  -e 'end tell'
