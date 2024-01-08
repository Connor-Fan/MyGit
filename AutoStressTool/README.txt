===========================================================================
Tool version 1.7.0, Python pakage 3.8.10, Product version 22621.2134
This is README.txt, the class material's top-level user guide
Author: Kanan Fan, https://www.youtube.com/channel/UCoSrY_IQQVpmIRZ9Xf-y93g
===========================================================================

Requirement:
Please install python-3.8.10-amd64.exe and the latest WDTF before run the stress tool
Note: please add an environment variable when you are installing Python

Command:
AutoStress.exe --cleanup No --setup --auto --standby 3 60 --hibernate 3 60 --wb 3 60 --cb 3 120
AutoStress.exe --cleanup No --setup --auto --standby 500 60
AutoStress.exe --cleanup No --setup --auto --hibernate 500 60
AutoStress.exe --cleanup No --setup --auto --wb 500 60
AutoStress.exe --cleanup No --setup --auto --cb 500 120

Command for --stop usage:
AutoStress.exe --cleanup No --setup --auto --standby 500 60 --stop all
AutoStress.exe --cleanup No --setup --auto --standby 500 60 --stop SanDisk
'all' is any device to add or lost that will be stop the program
'SanDisk' is a device name. If this device adds or losts, the program will be stopped

Troubleshooting:
Q: Show the error message that is ModuleNotFoundError: No module named 'encodings'
A: Please add an environment variable in your system when you are installing Python
Q: Show the error message that is AttributeError: module 'comtypes.gen.UIAutomationClient' has no attribute 'CUIAutomation' 
A: Please copy UIAutomationCore.dll to cover the old one from "C:\Windows\System32" to "C:\Users\xxx\Desktop\AutoStressTool"