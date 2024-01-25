===========================================================================
Tool version 2.6.2, Python package 3.8.10
This is README.txt, the class material's top-level user guide
Author: Kanan Fan, https://www.youtube.com/channel/UCoSrY_IQQVpmIRZ9Xf-y93g
===========================================================================
**Tool working path:**
C:\Users\Username\Desktop\AutoStressTool

Requirement:
Please install Python 3.8.10 (64-bit) and the latest WDTF before running the stress tool.
Note: Please add an environment variable when you are installing Python.

**Command:**
AutoStress.exe --cleanup No --setup --auto --standby 3 60 --hibernate 3 60 --wb 3 --cb 3 60 --delay 65
AutoStress.exe --cleanup No --setup --auto --standby 500 60 --delay 65
AutoStress.exe --cleanup No --setup --auto --hibernate 500 60 --delay 65
AutoStress.exe --cleanup No --setup --auto --wb 500 --delay 65
AutoStress.exe --cleanup No --setup --auto --cb 500 60 --delay 65
AutoStress.exe --cleanup No --setup --auto --greset 500 --delay 65

**Command for --stop usage:**
AutoStress.exe --cleanup No --setup --auto --cb 500 60 --delay 65 --stop all
AutoStress.exe --cleanup No --setup --auto --cb 500 60 --delay 65 --stop "Cirrus Logic" "SoundWire Speakers"
"all" is used as a wildcard, indicating that the program will be stopped if any device is added or lost.
"SoundWire Speakers" is a specific device name. If this device is either added or lost, the program will be stopped accordingly.

**Troubleshooting:**
Q: Show the error message of "ModuleNotFoundError: No module named 'encodings'".
A: Please add an environment variable when you are installing Python.
Q: Show the error message of "Can not run DeviceCompare! Please check it whether is ready for use. Error: (-2147220992, None, (None, None, None, 0, None))".
A: Please double-click AutoStress.exe to reset DeviceCompare.exe.
Q: Why I input "AutoStress.exe --cb 500 90", but the wake timer is actually set to 120s?
A: Auto On Time only supports minutes, so when using "AutoStress.exe --cb 500 90", the duration specified in seconds is automatically rounded to the nearest minute.