===========================================================================
Tool version 2.1.0, Python pakage 3.8.10
This is README.txt, the class material's top-level user guide
Author: Kanan Fan, https://www.youtube.com/channel/UCoSrY_IQQVpmIRZ9Xf-y93g
===========================================================================

Requirement:
Please install python-3.8.10-amd64.exe and the latest WDTF before run the stress tool
Note: please add an environment variable when you are installing Python

Command:
AutoStress.exe --cleanup No --setup --auto --standby 3 60 --hibernate 3 60 --wb 3 --cb 3 120 --delay 60
AutoStress.exe --cleanup No --setup --auto --standby 500 60 --delay 60
AutoStress.exe --cleanup No --setup --auto --hibernate 500 60 --delay 60
AutoStress.exe --cleanup No --setup --auto --wb 500 --delay 60
AutoStress.exe --cleanup No --setup --auto --cb 500 120 --delay 60

Command for --stop usage:
AutoStress.exe --cleanup No --setup --auto --standby 500 60 --delay 60 --stop all
AutoStress.exe --cleanup No --setup --auto --standby 500 60 --delay 60 --stop "SanDisk" "Cirrus Logic"
'all' is any device to add or lost that will be stop the program
'SanDisk' is a device name. If this device adds or losts, the program will be stopped

Troubleshooting:
Q: Show the error message of "ModuleNotFoundError: No module named 'encodings'" when AutoStress.exe was running
A: Please add an environment variable when you are installing Python
Q: Show the error message of "The test Failed in running --auto" when AutoStress.exe was running
A: Please double-click AutoStress.exe to reset DeviceCompare.exe