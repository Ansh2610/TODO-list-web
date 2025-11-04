@echo off
REM Startup script for SkillLens - Runs both FastAPI backend and Streamlit frontend

echo.
echo ========================================
echo   SkillLens Resume Analyzer
echo   Starting FastAPI + Streamlit
echo ========================================
echo.

REM Check if conda is available
where conda >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Conda not found. Please install Anaconda or Miniconda.
    pause
    exit /b 1
)

REM Activate conda environment
echo [1/3] Activating conda environment 'skills'...
call conda activate skills
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate 'skills' environment
    echo Please create it with: conda create -n skills python=3.11
    pause
    exit /b 1
)

echo.
echo [2/3] Starting FastAPI backend on port 8000...
start "SkillLens API" cmd /k "conda activate skills && uvicorn api.main:app --reload --port 8000"

REM Wait a bit for API to start
timeout /t 3 /nobreak >nul

echo.
echo [3/3] Starting Streamlit frontend on port 8501...
start "SkillLens UI" cmd /k "conda activate skills && streamlit run app_streamlit_simple.py"

echo.
echo ========================================
echo   SkillLens is starting!
echo ========================================
echo.
echo   API Documentation: http://localhost:8000/docs
echo   Streamlit UI:      http://localhost:8501
echo.
echo   Two terminal windows will open:
echo   - SkillLens API (FastAPI backend)
echo   - SkillLens UI (Streamlit frontend)
echo.
echo   Close this window or press Ctrl+C to exit
echo ========================================
echo.

pause
