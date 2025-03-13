@echo off

:: Parse arguments
set USE_CONDA=false
for %%A in (%*) do (
    if "%%A"=="--conda" set USE_CONDA=true
)

:: Check for Python 3.10
where python3.10 >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python 3.10 is not installed or --conda flag is used. Checking for Conda...
    where conda >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo Neither Python 3.10 nor Conda are installed! Install one and rerun the script.
        exit /b 1
    )
    echo Conda is installed. Using Conda to create an environment.
    if not exist "venv" (
        echo Creating Conda environment...
        conda create --yes --prefix "%CD%\venv" python=3.10
    ) else (
        echo Conda environment already exists.
    )
    call activate "%CD%\venv"
) else (
    echo Python 3.10 is installed. Using Python virtual environment.
    if not exist "venv" (
        echo Creating virtual environment...
        python3.10 -m venv venv
    ) else (
        echo Virtual environment already exists.
    )
    call venv\Scripts\activate
)

:: Install dependencies
if exist "requirements.txt" (
    echo Installing required packages...
    pip install --upgrade pip
    pip install -r requirements.txt
) else (
    echo requirements.txt file not found!
)

:: Deactivate virtual environment
if "%USE_CONDA%" == "true" (
    call conda deactivate
) else (
    call venv\Scripts\deactivate
)

echo Script completed.

