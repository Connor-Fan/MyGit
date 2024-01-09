===========================================================================
Tool version 2.5.4, Python package 3.8.10
This is README.txt, the class material's top-level user guide
Author: Kanan Fan, https://www.youtube.com/channel/UCoSrY_IQQVpmIRZ9Xf-y93g
===========================================================================

Requirement:
Please install Python 3.8.10 (64-bit) and the latest WDTF before running the stress tool.
Note: Please add an environment variable when you are installing Python.

Command:
AutoStress.exe --cleanup No --setup --auto --standby 3 60 --hibernate 3 60 --wb 3 --cb 3 60 --delay 65
AutoStress.exe --cleanup No --setup --auto --standby 500 60 --delay 65
AutoStress.exe --cleanup No --setup --auto --hibernate 500 60 --delay 65
AutoStress.exe --cleanup No --setup --auto --wb 500 --delay 65
AutoStress.exe --cleanup No --setup --auto --cb 500 90 --delay 65
AutoStress.exe --cleanup No --setup --auto --greset 500 --delay 65

Command for --stop usage:
AutoStress.exe --cleanup No --setup --auto --cb 500 60 --delay 65 --stop all
AutoStress.exe --cleanup No --setup --auto --cb 500 60 --delay 65 --stop "Cirrus Logic" "SoundWire Speakers"
'all' is any device to add or lost that will be stopped the program.
'SoundWire Speakers' is a device name. If this device adds or is lost, the program will be stopped.

Troubleshooting:
Q: Show the error message of "ModuleNotFoundError: No module named 'encodings'" when AutoStress.exe was running.
A: Please add an environment variable when you are installing Python.
Q: Show the error message of "The test Failed in running --auto" when AutoStress.exe was running.
A: Please double-click AutoStress.exe to reset DeviceCompare.exe.