@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-system.ps1" %*
endlocal
