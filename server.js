const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 8080;
const ROOT = __dirname;
const MEMORY_PATH = path.join(ROOT, "memory", "user_memory.json");
const LLAMA_SERVER_URL = process.env.LLAMA_SERVER_URL || "http://127.0.0.1:8081/completion";

const MIME_TYPES = {
  ".html": "text/html",
  ".css": "text/css",
  ".js": "application/javascript",
  ".json": "application/json",
  ".gitkeep": "text/plain",
};

function buildDefaultMemory() {
  return {
    summary: "",
    facts: [],
    preferences: [],
    keywords: [],
    emotion_patterns: {},
    last_updated: null,
  };
}

function normalizeMemory(memory) {
  return {
    summary: memory?.summary || "",
    facts: Array.isArray(memory?.facts) ? memory.facts : [],
    preferences: Array.isArray(memory?.preferences) ? memory.preferences : [],
    keywords: Array.isArray(memory?.keywords) ? memory.keywords : [],
    emotion_patterns: memory?.emotion_patterns && typeof memory.emotion_patterns === "object"
      ? memory.emotion_patterns
      : {},
    last_updated: memory?.last_updated || null,
  };
}

function sendJSON(res, status, data) {
  const payload = JSON.stringify(data);
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(payload);
}

function serveStatic(req, res) {
  const reqPath = req.url === "/" ? "/index.html" : req.url;
  const filePath = path.join(ROOT, decodeURIComponent(reqPath.split("?")[0]));

  if (!filePath.startsWith(ROOT)) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end("Not Found");
      return;
    }
    const ext = path.extname(filePath);
    res.writeHead(200, { "Content-Type": MIME_TYPES[ext] || "application/octet-stream" });
    res.end(data);
  });
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = "";
    req.on("data", (chunk) => {
      body += chunk;
    });
    req.on("end", () => {
      try {
        const parsed = JSON.parse(body || "{}");
        resolve(parsed);
      } catch (error) {
        reject(error);
      }
    });
  });
}

async function handleChat(req, res) {
  try {
    const payload = await readBody(req);
    const response = await fetch(LLAMA_SERVER_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: `${payload.prompt}\nUSER: ${payload.message}\nASSISTANT:`,
        n_predict: payload.max_tokens || 256,
        temperature: payload.temperature ?? 0.7,
        stop: payload.stop || ["USER:", "SYSTEM:"],
      }),
    });

    if (!response.ok) {
      sendJSON(res, 502, { reply: "Model lokal tidak tersedia." });
      return;
    }

    const data = await response.json();
    const reply = data.content || data.reply || "(Tidak ada jawaban)";
    sendJSON(res, 200, { reply });
  } catch (error) {
    sendJSON(res, 500, { reply: "Model lokal belum siap." });
  }
}

async function handleMemory(req, res) {
  if (req.method === "GET") {
    fs.readFile(MEMORY_PATH, "utf8", (err, data) => {
      if (err) {
        const fallback = buildDefaultMemory();
        fs.writeFile(MEMORY_PATH, JSON.stringify(fallback, null, 2), () => {
          sendJSON(res, 200, fallback);
        });
        return;
      }
      try {
        const parsed = JSON.parse(data);
        const normalized = normalizeMemory(parsed);
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify(normalized));
      } catch (error) {
        const fallback = buildDefaultMemory();
        fs.writeFile(MEMORY_PATH, JSON.stringify(fallback, null, 2), () => {
          sendJSON(res, 200, fallback);
        });
      }
    });
    return;
  }

  if (req.method === "POST") {
    try {
      const payload = await readBody(req);
      const normalized = normalizeMemory(payload);
      fs.writeFile(MEMORY_PATH, JSON.stringify(normalized, null, 2), (err) => {
        if (err) {
          sendJSON(res, 500, { ok: false });
          return;
        }
        sendJSON(res, 200, { ok: true });
      });
    } catch (error) {
      sendJSON(res, 400, { ok: false });
    }
  }
}

const server = http.createServer((req, res) => {
  if (req.url.startsWith("/api/chat")) {
    handleChat(req, res);
    return;
  }

  if (req.url.startsWith("/api/memory")) {
    handleMemory(req, res);
    return;
  }

  serveStatic(req, res);
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`Server berjalan di http://127.0.0.1:${PORT}`);
  console.log(`Pastikan inference server llama.cpp berjalan di ${LLAMA_SERVER_URL}`);
});
