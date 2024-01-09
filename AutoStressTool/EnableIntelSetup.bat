echo off
rem ########################################
rem    #          請自行更新測試軟體        #
rem ########################################

set MFG_DIR=MfgTools
set HOTSOS_DIR=HotSOS
set SAFE_DIR=SafeAuthClient
set "desktopPath=%userprofile%\Desktop"
set SAFESRV=192.168.8.7
set SAFELOG=safe.log

set "params=%*"
cd /d "%~dp0" && ( if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs" ) && fsutil dirty query %systemdrive% 1>nul 2>nul || (  echo Set UAC = CreateObject^("Shell.Application"^) : UAC.ShellExecute "cmd.exe", "/k cd ""%~sdp0"" && %~s0 %params%", "", "runas", 1 >> "%temp%\getadmin.vbs" && "%temp%\getadmin.vbs" && exit /B )

REM Prompt the user to enter a string
echo 1 is that doesn't need to bypass Dell safe mode
echo 2 is that needs to bypass Dell safe mode
set /p input=Please enter a number to enable Intel Advanced Setup(1~2): 

REM Use IF statements to check the input string and determine the cases
if "%input%"=="1" goto :case1
if "%input%"=="2" goto :case2

REM If the input string doesn't match any case, execute the default case
goto :default

REM ########################################
:case1
echo You entered case1

cd /d "%~dp0"

cd %MFG_DIR%
MfgMode64W.exe +ENMM
PlatCfg64W.exe 0x0548:0x0001

@echo.

echo Please press any key to restart your system
pause
shutdown -r -t 0 -f

goto :end

REM ########################################
:case2
echo You entered case2

cd /d "%~dp0"

cd %SAFE_DIR%
if exist %SAFELOG% del %SAFELOG%

REM Ping the safe server to ensure connection is established
ping %SAFESRV% -n 1 | find /I "Reply from %SAFESRV%: bytes=32"

SafeAuthClient64W.exe -log %SAFELOG% -safe %SAFESRV%
	if %Errorlevel% == 12 goto safe_fail

cd /d "%~dp0"
echo Please press any key to enable Intel Advanced Setup
pause

cd /d "%~dp0"

cd %MFG_DIR%
MfgMode64W.exe +ENMM
PlatCfg64W.exe 0x0548:0x0001

@echo.

echo Please press any key to restart your system
pause
shutdown -r -t 0 -f

goto :end

:default
echo The input string doesn't match any case

:safe_fail
echo Cann't ping to the safe server. Please check whether the safe server is ready

:end
REM End the script
pause
exit