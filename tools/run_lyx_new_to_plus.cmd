@echo off
setlocal DisableDelayedExpansion
title Theorems (AMS) Plus
set "PYTHONUTF8=1"
set "PYTHONDONTWRITEBYTECODE=1"
set "LYX_PLUS_LAUNCHER=1"
call "%~dp0find_python.cmd"
if not defined LYX_PLUS_RUN goto missing_python
%LYX_PLUS_RUN% -B "%~dp0lyx_new_to_plus.py" %*
set "LYX_PLUS_EXIT=%errorlevel%"
goto finished
:missing_python
echo The Python bundled with LyX 2.5 or Python 3.10+ could not be found.
echo Check your LyX installation, or run the script with its Python\python.exe.
set "LYX_PLUS_EXIT=1"
:finished
echo.
pause
exit /b %LYX_PLUS_EXIT%
