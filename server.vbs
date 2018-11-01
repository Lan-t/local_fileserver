Option Explicit
 
Const vbHide = 0            
Const vbNormalFocus = 1 
 
Dim objWShell
Set objWShell = CreateObject("WScript.Shell")
objWShell.Run "cmd /c python Server.py >> log 2>&1", vbHide, False
 
Set objWShell = Nothing