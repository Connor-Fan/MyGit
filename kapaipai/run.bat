@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"

call :find_python
if errorlevel 1 goto python_missing

:menu
cls
echo ============================================================
echo Ruten to Kapaipai Workflow
echo ============================================================
echo [1] Export Ruten store products to Excel
echo [2] Generate Kapaipai upload preview
echo [3] Start Kapaipai upload
echo [Q] Quit
echo.
choice /c 123Q /n /m "Select an option: "
if errorlevel 4 exit /b 0
if errorlevel 3 goto upload
if errorlevel 2 goto preview
if errorlevel 1 goto export
goto menu

:export
cls
echo [Case 1] Export Ruten store products to Excel
echo.
set "STORE_URL="
set /p "STORE_URL=Enter or paste the Ruten store URL: "
set "STORE_URL=%STORE_URL:"=%"
if not defined STORE_URL (
    echo.
    echo A Ruten store URL is required.
    echo.
    pause
    goto menu
)
call :run_python "ruten_exporter.py" --store-url "%STORE_URL%"
set "RUN_RESULT=%ERRORLEVEL%"
call :show_result "Ruten export"
goto menu

:preview
cls
echo [Case 2] Generate Kapaipai upload preview
echo.
set "INPUT_FILE="
set /p "INPUT_FILE=Enter or drag the Ruten Excel path here, or press Enter to use the latest file: "
set "INPUT_FILE=%INPUT_FILE:"=%"
call :run_python "kapaipai_uploader.py" --input "%INPUT_FILE%"
set "RUN_RESULT=%ERRORLEVEL%"
call :show_result "Preview generation"
goto menu

:upload
cls
echo [Case 3] Start Kapaipai upload
echo.
set "INPUT_FILE="
set /p "INPUT_FILE=Enter or drag the Ruten Excel path here, or press Enter to use the latest file: "
set "INPUT_FILE=%INPUT_FILE:"=%"
call :run_python "kapaipai_uploader.py" --input "%INPUT_FILE%" --execute --yes
set "RUN_RESULT=%ERRORLEVEL%"
call :show_result "Kapaipai upload"
goto menu

:find_python
where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_EXE=py"
    exit /b 0
)
where python >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_EXE=python"
    exit /b 0
)
exit /b 1

:run_python
%PYTHON_EXE% -X utf8 %*
exit /b %ERRORLEVEL%

:show_result
echo.
if "%RUN_RESULT%"=="0" (
    echo %~1 completed successfully.
) else (
    echo %~1 failed. Error code: %RUN_RESULT%
)
echo.
pause
exit /b 0

:python_missing
echo Python was not found.
echo Install Python 3.11 or later and enable "Add python.exe to PATH".
echo.
pause
exit /b 1
