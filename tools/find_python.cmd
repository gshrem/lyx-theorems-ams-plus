@echo off
rem Sets LYX_PLUS_RUN to a Python 3.10+ command, preferring the Python bundled with LyX 2.5.
rem Official LyX installer: SOFTWARE\LyX, InstDir25; HKCU or HKLM.
set "LYX_PLUS_RUN="
for %%H in (HKCU HKLM) do for %%V in (64 32) do for /f "tokens=2,*" %%A in ('%SystemRoot%\System32\reg.exe query "%%H\SOFTWARE\LyX" /v InstDir25 /reg:%%V 2^>nul ^<nul') do if /I "%%A"=="REG_SZ" if not defined LYX_PLUS_RUN call :try_file "%%B\Python\python.exe"
for %%D in ("%LOCALAPPDATA%\Programs" "%ProgramW6432%" "%ProgramFiles%" "%ProgramFiles(x86)%") do if not defined LYX_PLUS_RUN call :try_file "%%~D\LyX 2.5\Python\python.exe"
if not defined LYX_PLUS_RUN where python.exe >nul 2>&1 && python -B -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>&1 && set "LYX_PLUS_RUN=python"
if not defined LYX_PLUS_RUN where py.exe >nul 2>&1 && py -3 -B -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>&1 && set "LYX_PLUS_RUN=py -3"
exit /b 0

:try_file
if exist "%~1" "%~1" -B -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>&1 && set "LYX_PLUS_RUN="%~1""
exit /b 0
