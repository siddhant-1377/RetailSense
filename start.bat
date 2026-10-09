@echo off
setlocal
cd /d "%~dp0"
echo Starting RetailSense (backend + frontend)...
npm run dev
endlocal
