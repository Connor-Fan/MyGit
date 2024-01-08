@echo off
@rem ########################################
@rem #          請自行更新測試軟體          #
@rem ########################################

@set "params=%*"
cd /d "%~dp0" && ( if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs" ) && fsutil dirty query %systemdrive% 1>nul 2>nul || (  echo Set UAC = CreateObject^("Shell.Application"^) : UAC.ShellExecute "cmd.exe", "/k cd ""%~sdp0"" && %~s0 %params%", "", "runas", 1 >> "%temp%\getadmin.vbs" && "%temp%\getadmin.vbs" && exit /B )

:: go back to the workplace
cd /d "%~dp0"

@echo ==========================================================
@echo ======Please enter 1 or 2 to be with/without in ICON======
@echo =========(1)within ICON (2)without ICON (3)clean =========
@echo ==========================================================

@set /p var=PleaseEnterVar:
if "%var%" == "1" (
    goto :Within
) else if "%var%"== "2" (
    goto :Without
) else if "%var%"== "3" (
    goto :Clean
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

pause
exit

:Error
@echo Please re-type a correct argument again
pause
exit