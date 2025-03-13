@echo off

:: Parse arguments
set USE_CONDA=false
for %%A in (%*) do (
    if "%%A"=="--conda" set USE_CONDA=true
)

:: Activate the appropriate environment
if "%USE_CONDA%"=="true" (
    echo Activating Conda environment...
    where conda >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo Conda is not installed! Install Conda and try again.
        exit /b 1
    )
    call conda activate venv
) else (
    if exist "venv" (
        echo Activating virtual environment...
        call venv\Scripts\activate
    ) else (
        echo Virtual environment does not exist! Run setup script first.
        exit /b 1
    )
)

:: Handle script interruption (CTRL+C) and ensure environment deactivation
setlocal EnableDelayedExpansion
for /f "tokens=2 delims==" %%I in ('"mode con"') do set "cols=%%I"
if %cols% GTR 0 (
    echo Use CTRL+BREAK to properly exit and deactivate environment.
)

:: Run webui.py
if exist "webui.py" (
    echo Starting web UI...
    python webui.py
) else (
    echo webui.py not found!
    exit /b 1
)

:: Deactivate virtual environment after execution
if "%USE_CONDA%"=="true" (
    call conda deactivate
) else (
    call venv\Scripts\deactivate
)

echo Script completed.
