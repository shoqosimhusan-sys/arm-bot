Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

userProfile = WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%")
pythonExe = userProfile & "\Programs\Python\Python312\python.exe"

scriptDir = "C:\Users\xxxxx\Downloads\ARM baza\arm_bot"
botScript = scriptDir & "\bot.py"

If fso.FileExists(pythonExe) Then
    WshShell.CurrentDirectory = scriptDir
    WshShell.Run """" & pythonExe & """ """ & botScript & """", 0, False
End If
