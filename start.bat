@echo off
setlocal
python --version >nul 2>nul
if errorlevel 1 (
  echo Python tidak ditemukan. Install Python 3.10+
  exit /b 1
)
python -m venv .venv
call .venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
flask --app app.py init-db
python app.py
