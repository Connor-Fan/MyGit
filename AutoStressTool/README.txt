===========================================================================
Tool version 1.3.0, Python pakage 3.11.0, Product version 10.0.22621.755
This is README.txt, the class material's top-level user guide
Author: Kanan Fan, https://www.youtube.com/channel/UCoSrY_IQQVpmIRZ9Xf-y93g
===========================================================================

Requirement:
Install python-3.11.0-amd64.exe and WDTF
Note: please add an environment variable when you are installing Python

Command:
AutoStress.exe --cleanup --setup --auto --standby 3 60 --hibernate 3 60 --wb 3 60 --cb 3 120
AutoStress.exe --cleanup --setup --auto --standby 500 60
AutoStress.exe --cleanup --setup --auto --hibernate 500 90
AutoStress.exe --cleanup --setup --auto --wb 500 60
AutoStress.exe --cleanup --setup --auto --cb 500 120

Troubleshooting:
Q: Show the error message that is ModuleNotFoundError: No module named 'encodings'
A: Please add an environment variable in your system when you are installing Python
Q: Show the error message that is AttributeError: module 'comtypes.gen.UIAutomationClient' has no attribute 'CUIAutomation' 
A: Please copy UIAutomationCore.dll to cover the old one from "C:\Windows\System32" to "C:\Users\xxx\Desktop\AutoStressTool"