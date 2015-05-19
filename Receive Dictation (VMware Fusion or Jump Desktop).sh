#!/bin/zsh

# note - requires appswitch 1.1.2 or later, currently unreleased but available from GitHub

FRONT_PID=$(appswitch -P)
/usr/local/bin/appswitch -h
/usr/local/bin/appswitch -sp $FRONT_PID
