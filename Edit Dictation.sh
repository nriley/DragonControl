#!/bin/zsh -f

APPSWITCH=/usr/local/bin/appswitch

$APPSWITCH -i com.p5sys.jump.mac.viewer || $APPSWITCH -i com.vmware.fusion
