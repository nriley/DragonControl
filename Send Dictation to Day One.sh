#!/bin/zsh -ef

${0:h}/word_dictation_document.py | \
	/usr/local/bin/dayone \
	-j=~'/Library/Group Containers/5U8NS4GX82.dayoneapp2/Data/Auto Import/Default Journal.dayone' \
	new

${0:h}/clear_dictation.py
