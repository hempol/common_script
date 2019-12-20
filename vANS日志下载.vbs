Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd",9
WScript.Sleep 500
WshShell.SendKeys "+"
WScript.Sleep 500
WshShell.SendKeys "pscp -P 9922 -pw raisecom!@#$ root@192.168.193.40:/var/log/nfv/netconf/netconf.log.0 C:\Users\hempol\Desktop\Files"
WshShell.SendKeys "{ENTER}"
WScript.Sleep 1500
WshShell.SendKeys "y"
WshShell.SendKeys "{ENTER}"
WScript.Sleep 1500
WshShell.SendKeys "exit"
WshShell.SendKeys "{ENTER}"
Set WshShell = Nothing
