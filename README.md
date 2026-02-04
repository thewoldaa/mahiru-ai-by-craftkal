# Mahiru Companion (Offline)

Aplikasi AI companion offline berbasis Pygmalion-2-7B (GGUF) yang berjalan di localhost.
Semua komponen berjalan lokal tanpa API eksternal atau CDN.

## Struktur Folder

```
index.html
style.css
script.js
server.js
models/pygmalion-2-7b.Q2_K.gguf.gitkeep
memory/user_memory.json
assets/
  idle.png.gitkeep
  talk.png.gitkeep
  happy.png.gitkeep
  sad.png.gitkeep
  sleep.png.gitkeep
  room.png.gitkeep
```

## Cara Menjalankan (Offline)

1. **Pastikan model GGUF tersedia.**
   - Letakkan file model asli di folder `models/`.
   - Ganti placeholder `models/pygmalion-2-7b.Q2_K.gguf.gitkeep` dengan file model asli bernama `pygmalion-2-7b.Q2_K.gguf`.

2. **Jalankan server inference lokal** (contoh: `llama.cpp` server).
   - Jalankan server inference di `http://127.0.0.1:8081/completion` atau set env `LLAMA_SERVER_URL`.

3. **Jalankan server frontend lokal.**
   ```bash
   node server.js
   ```

4. **Buka aplikasi di browser.**
   - `http://127.0.0.1:8080`

## Catatan

- UI memakai placeholder `.gitkeep` untuk assets dan background. Ganti dengan asset asli sesuai kebutuhan.
- Memori disimpan lokal di `memory/user_memory.json`.
- Endpoint lokal:
  - `GET/POST /api/memory` untuk memori.
  - `POST /api/chat` untuk chat ke server inference lokal.
