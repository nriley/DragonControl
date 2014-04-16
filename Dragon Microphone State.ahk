#NoEnv
#NoTrayIcon
#Persistent
#SingleInstance Force
#Warn

If 0 <> 1
	ExitApp

If 1 = on
	ExitApp
else
	Progress, y0 zh0 ctFF0000 cw000000 fm8 b0 h20 zy4, , Dragon Not Listening, , Tahoma
