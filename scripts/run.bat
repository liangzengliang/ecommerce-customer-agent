@echo off
chcp 65001 >nul
setlocal

set "PROJECT_ROOT=%~dp0.."
pushd "%PROJECT_ROOT%"
set "PROJECT_ROOT=%CD%"
popd

set "BACKEND_DIR=%PROJECT_ROOT%\backend"
set "FRONTEND_DIR=%PROJECT_ROOT%\frontend"
set "LOG_DIR=%PROJECT_ROOT%\logs"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

if "%~1"=="" goto usage
if /i "%~1"=="backend"  goto start_backend
if /i "%~1"=="frontend" goto start_frontend
if /i "%~1"=="all"      goto start_all
goto usage

:start_backend
echo [INFO] Starting backend...
cd /d "%BACKEND_DIR%"
call "%PROJECT_ROOT%\venv\Scripts\activate.bat"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
goto end

:start_frontend
echo [INFO] Starting frontend...
cd /d "%FRONTEND_DIR%"
npm run dev
goto end

:start_all
echo [INFO] Starting backend and frontend...

start "Backend" cmd /k "cd /d "%BACKEND_DIR%" && call "%PROJECT_ROOT%\venv\Scripts\activate.bat" && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

start "Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && npm run dev"

echo [INFO] Backend and frontend started in separate windows.
echo [INFO] Close those windows to stop services.
goto end

:usage
echo Usage: %~nx0 {backend^|frontend^|all}
goto end

:end
endlocal