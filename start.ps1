$ErrorActionPreference = "Stop"
$python = "python"

try {
  & $python --version
} catch {
  Write-Host "Python tidak ditemukan. Install Python 3.10+" -ForegroundColor Red
  exit 1
}

& $python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
flask --app app.py init-db
python app.py
