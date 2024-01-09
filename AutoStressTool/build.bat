@echo off
@rem ########################################
@rem   #          請自行更新測試軟體          #
@rem ########################################

set SIGNTOOL_DIR=DigitalSignature
set AutoStress_DIR=C:\BIOS\MyGit\AutoStressTool
set DIST_DIR=dist

@set "params=%*"
cd /d "%~dp0" && ( if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs" ) && fsutil dirty query %systemdrive% 1>nul 2>nul || (  echo Set UAC = CreateObject^("Shell.Application"^) : UAC.ShellExecute "cmd.exe", "/k cd ""%~sdp0"" && %~s0 %params%", "", "runas", 1 >> "%temp%\getadmin.vbs" && "%temp%\getadmin.vbs" && exit /B )

:: go back to the workplace
cd /d "%~dp0"

@echo ================================================================
@echo ======Please enter 1, 2, 3 or 4 to select your next action======
@echo ==(1)Within ICON (2)Without ICON (3)Clean (4)Digital Signature==
@echo ================================================================

@set /p var=PleaseEnterVar:
if "%var%" == "1" (
    goto :Within
) else if "%var%"== "2" (
    goto :Without
) else if "%var%"== "3" (
    goto :Clean
) else if "%var%"== "4" (
    goto :Sign
) else (
    goto :Error
)

:Within
pyinstaller -c -F AutoStress.py --icon guraSmirk.ico --hidden-import win32timezone
pause
exit

:Without
pyinstaller -c -F AutoStress.py --hidden-import win32timezone
pause
exit

:Clean
rmdir /s /q build && echo Deletion Successful
rmdir /s /q dist && echo Deletion Successful
del AutoStress.spec && echo Deletion Successful
cd %SIGNTOOL_DIR%
del AutoStress.exe && echo Deletion Successful
pause
exit

:Sign
cd %DIST_DIR%
copy AutoStress.exe %~dp0%SIGNTOOL_DIR%
echo File copied to dist folder successfully!
:: go back to the workplace
cd /d "%~dp0"
cd %SIGNTOOL_DIR%
signtool.exe sign /fd certHash /f YourCertificate.pfx /p ZAQ!2wsx AutoStress.exe
signtool.exe verify /pa /v AutoStress.exe
copy AutoStress.exe %AutoStress_DIR%
echo File copied to the stress folder successfully!
pause
exit

:Error
@echo Please re-type a correct argument again
pause
exit