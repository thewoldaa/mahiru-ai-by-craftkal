#!/usr/bin/env bash
set -e

PYTHON_BIN=${PYTHON_BIN:-python3}

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python tidak ditemukan. Install Python 3.10+ terlebih dahulu."
  exit 1
fi

VERSION=$($PYTHON_BIN -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python version: $VERSION"

$PYTHON_BIN -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

flask --app app.py init-db || true

echo "Menjalankan server di http://localhost:5000"
python app.py
