# Adik Tiri yang Nakal - Full Visual Novel (Flask)

Proyek Visual Novel berbasis **Flask + Flask-SocketIO + SQLAlchemy** dengan 10 chapter, sistem save/load, achievements, inventory, relationship, dan multiple ending.

## Fitur Utama
- Authentication (register/login/logout)
- Scene engine JSON (10 chapter × 10 scene sample)
- Choice system dengan perubahan stat dan flag
- Save/load 20 slot per user
- Achievement 30+ definisi
- Inventory API
- WebSocket events (scene_update, expression_change, achievement_unlocked)
- Settings persistence
- Export/import save
- Responsive UI (desktop/tablet/mobile)

## Quick Start

### Linux/macOS
```bash
chmod +x start.sh
./start.sh
```

### Windows PowerShell
```powershell
./start.ps1
```

### Manual
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app app.py init-db
python app.py
```

Akses: http://localhost:5000

## API Endpoint
- `GET /api/scene/<scene_id>`
- `POST /api/choice`
- `POST /api/save`
- `GET /api/load/<slot>`
- `GET /api/inventory`
- `POST /api/inventory/use`
- `GET /api/achievements`
- `GET /api/gallery`
- `GET /api/characters`
- `POST /api/settings`

## Struktur
Lihat spesifikasi direktori pada prompt; semua folder inti sudah dibuat dan berisi sample data siap jalan.

## Testing
```bash
pytest -q
```

## Deployment
- Docker: `docker compose up --build`
- PythonAnywhere/Heroku: gunakan `app.py` sebagai WSGI entry

## Catatan Konten
Cerita bersifat 15+, tanpa konten eksplisit, berbahasa Indonesia.
