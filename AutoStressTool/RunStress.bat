echo off
rem ########################################
rem    #          請自行更新測試軟體        #
rem ########################################

set "STRESS_DIR=%USERPROFILE%\Desktop\AutoStressTool"

set "params=%*"
cd /d "%~dp0" && ( if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs" ) && fsutil dirty query %systemdrive% 1>nul 2>nul || (  echo Set UAC = CreateObject^("Shell.Application"^) : UAC.ShellExecute "cmd.exe", "/k cd ""%~sdp0"" && %~s0 %params%", "", "runas", 1 >> "%temp%\getadmin.vbs" && "%temp%\getadmin.vbs" && exit /B )

REM Prompt the user to enter a string
echo (1) is running standby cycles
echo (2) is running hibernate cycles
echo (3) is running warm boot cycles
echo (4) is running cold boot cycles
set /p input=Please enter a number(1~4): 

REM Use IF statements to check the input string and determine the cases
if "%input%"=="1" goto :case1
if "%input%"=="2" goto :case2
if "%input%"=="3" goto :case3
if "%input%"=="4" goto :case4

REM If the input string doesn't match any case, execute the default case
goto :default

rem ########################################
:case1
echo You entered case1

cd /d "%~dp0"
AutoStress.exe --cleanup No --setup --auto --standby 500 60 --delay 65
goto :end

rem ########################################
:case2
echo You entered case2

cd /d "%~dp0"
AutoStress.exe --cleanup No --setup --auto --hibernate 500 60 --delay 65
goto :end

rem ########################################
:case3
echo You entered case3

cd /d "%~dp0"
AutoStress.exe --cleanup No --setup --auto --wb 500 --delay 65
goto :end

rem ########################################
:case4
echo You entered case4

cd /d "%~dp0"
AutoStress.exe --cleanup No --setup --auto --cb 500 90 --delay 65
goto :end

:default
echo The input string doesn't match any case

:end
REM End the script
pause
exit