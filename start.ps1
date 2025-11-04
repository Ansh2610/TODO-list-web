# Startup script for SkillLens - Runs both FastAPI backend and Streamlit frontend

Write-Host ""
Write-Host "========================================"
Write-Host "  SkillLens Resume Analyzer"
Write-Host "  Starting FastAPI + Streamlit"
Write-Host "========================================"
Write-Host ""

# Check if conda is available
$condaExists = Get-Command conda -ErrorAction SilentlyContinue
if (-not $condaExists) {
    Write-Host "ERROR: Conda not found. Please install Anaconda or Miniconda." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[1/3] Activating conda environment 'skills'..." -ForegroundColor Cyan
conda activate skills
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate 'skills' environment" -ForegroundColor Red
    Write-Host "Please create it with: conda create -n skills python=3.11" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[2/3] Starting FastAPI backend on port 8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "conda activate skills; uvicorn api.main:app --reload --port 8000" -WindowStyle Normal

# Wait for API to start
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "[3/3] Starting Streamlit frontend on port 8501..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "conda activate skills; streamlit run app_streamlit_simple.py" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  SkillLens is starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Streamlit UI:      http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "  Two terminal windows will open:" -ForegroundColor Yellow
Write-Host "  - FastAPI backend (port 8000)" -ForegroundColor Yellow
Write-Host "  - Streamlit frontend (port 8501)" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Your browser should open automatically." -ForegroundColor Cyan
Write-Host "  Close the terminal windows to stop the servers." -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Green

Read-Host "Press Enter to close this window"
