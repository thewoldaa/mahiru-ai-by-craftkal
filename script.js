const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const characterImage = document.getElementById("character");
const statusEl = document.getElementById("status");

const EXPRESSION_MAP = {
  idle: "assets/idle.png.gitkeep",
  talk: "assets/talk.png.gitkeep",
  happy: "assets/happy.png.gitkeep",
  sad: "assets/sad.png.gitkeep",
  sleep: "assets/sleep.png.gitkeep",
};

const SYSTEM_PROMPT = `Kamu adalah companion AI yang terinspirasi Mahiru: tenang, cerdas, perhatian, dan praktis. Kamu tidak genit, tidak romantis, tidak menggoda, dan tidak mengklaim kepemilikan user. Jawaban harus rapi, lembut tapi tegas, fokus membantu dan menemani berpikir. Jika informasi tidak jelas, minta klarifikasi. Jangan mengada-ada. Gunakan memori percakapan untuk konsistensi, tetapi jangan menyebut sistem internal.`;

const STATE = {
  shortTerm: [],
  longTerm: {
    summary: "",
    facts: [],
    preferences: [],
    keywords: [],
    emotion_patterns: {},
    last_updated: null,
  },
  interactionCount: 0,
  sleepTimer: null,
};

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

const POSITIVE_WORDS = ["senang", "bahagia", "suka", "bagus", "mantap", "terima kasih", "puas", "lega"];
const NEGATIVE_WORDS = ["sedih", "kesal", "marah", "kecewa", "capek", "bingung", "khawatir", "lelah"];
const STOP_WORDS = [
  "yang",
  "dan",
  "dengan",
  "atau",
  "untuk",
  "pada",
  "dari",
  "saya",
  "aku",
  "kamu",
  "kita",
  "ini",
  "itu",
  "ada",
  "jadi",
  "juga",
  "lagi",
  "karena",
  "seperti",
  "tentang",
];

function setStatus(message) {
  statusEl.textContent = message;
}

function setExpression(state) {
  characterImage.src = EXPRESSION_MAP[state] || EXPRESSION_MAP.idle;
}

function resetSleepTimer() {
  if (STATE.sleepTimer) {
    window.clearTimeout(STATE.sleepTimer);
  }
  STATE.sleepTimer = window.setTimeout(() => {
    setExpression("sleep");
    setStatus("Mahiru sedang diam sejenak.");
  }, 45000);
}

function appendMessage(role, text) {
  const bubble = document.createElement("div");
  bubble.className = `message ${role}`;
  bubble.textContent = text;
  chatLog.appendChild(bubble);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function sentimentScore(text) {
  const lower = text.toLowerCase();
  let score = 0;
  POSITIVE_WORDS.forEach((word) => {
    if (lower.includes(word)) score += 1;
  });
  NEGATIVE_WORDS.forEach((word) => {
    if (lower.includes(word)) score -= 1;
  });
  return score;
}

function extractKeywords(text, limit = 5) {
  const words = text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((word) => word.length > 3 && !STOP_WORDS.includes(word));

  const counts = words.reduce((acc, word) => {
    acc[word] = (acc[word] || 0) + 1;
    return acc;
  }, {});

  return Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([word]) => word);
}

function updateLongTermMemory(input) {
  const lower = input.toLowerCase();
  const facts = [];
  const preferences = [];
  const keywords = extractKeywords(input, 6);

  if (lower.includes("saya") || lower.includes("aku")) {
    if (lower.includes("saya bekerja") || lower.includes("aku bekerja")) {
      facts.push(input);
    }
    if (lower.includes("tinggal di")) {
      facts.push(input);
    }
    if (lower.includes("saya suka") || lower.includes("aku suka")) {
      preferences.push(input);
    }
    if (lower.includes("hobi")) {
      preferences.push(input);
    }
  }

  if (facts.length) {
    STATE.longTerm.facts = [...new Set([...STATE.longTerm.facts, ...facts])];
  }
  if (preferences.length) {
    STATE.longTerm.preferences = [...new Set([...STATE.longTerm.preferences, ...preferences])];
  }
  if (keywords.length) {
    STATE.longTerm.keywords = [...new Set([...STATE.longTerm.keywords, ...keywords])];
  }

  if (facts.length || preferences.length) {
    STATE.longTerm.last_updated = new Date().toISOString();
  }
}

function summarizeShortTerm() {
  const recent = STATE.shortTerm.slice(-6);
  return recent.map((entry) => `${entry.role}: ${entry.text}`).join(" | ");
}

function analyzeInput(input) {
  const score = sentimentScore(input);
  const lengthScore = Math.min(input.length / 80, 1);
  const emotionScore = Math.min(Math.abs(score) / 3, 1);
  const interactionScore = Math.min(STATE.interactionCount / 10, 1);
  const potentialScore = (lengthScore * 0.4 + emotionScore * 0.3 + interactionScore * 0.3);

  const tone = score > 0 ? "hangat" : score < 0 ? "menenangkan" : "netral";
  const shouldRemember = /saya|aku|hobi|kerja|tinggal|suka/.test(input.toLowerCase());
  const goal = input.endsWith("?") ? "menjawab dengan jelas" : "memberi tanggapan terstruktur";
  const responseStyle = potentialScore > 0.6 ? "mendalam" : "ringkas";
  const followUp = potentialScore > 0.5;
  const maxTokens = potentialScore > 0.65 ? 320 : potentialScore > 0.4 ? 220 : 140;

  return {
    tone,
    goal,
    shouldRemember,
    responseStyle,
    followUp,
    potentialScore,
    maxTokens,
  };
}

function buildPrompt(analysis) {
  const memorySummary = STATE.longTerm.summary || "Belum ada ringkasan.";
  const facts = STATE.longTerm.facts.length ? STATE.longTerm.facts.join("; ") : "Tidak ada fakta tersimpan.";
  const prefs = STATE.longTerm.preferences.length ? STATE.longTerm.preferences.join("; ") : "Tidak ada preferensi tersimpan.";
  const keywords = STATE.longTerm.keywords.length ? STATE.longTerm.keywords.join(", ") : "Belum ada keyword.";
  const emotionPatterns = Object.keys(STATE.longTerm.emotion_patterns).length
    ? JSON.stringify(STATE.longTerm.emotion_patterns)
    : "Belum ada pola emosi.";

  return `SYSTEM: ${SYSTEM_PROMPT}
MEMORY SUMMARY: ${memorySummary}
LONG TERM FACTS: ${facts}
LONG TERM PREFERENCES: ${prefs}
KEYWORDS: ${keywords}
EMOTION PATTERNS: ${emotionPatterns}
SHORT TERM: ${summarizeShortTerm()}

ANALYSIS: Tujuan=${analysis.goal}; Nada=${analysis.tone}; Gaya=${analysis.responseStyle}; FollowUp=${analysis.followUp}

INSTRUCTION: Balas sebagai Mahiru yang konsisten, sesuai analisis. Jika FollowUp=true, akhiri dengan satu pertanyaan ringan untuk melanjutkan diskusi. Jangan menyebutkan bagian SYSTEM atau MEMORY.`;
}

async function loadMemory() {
  try {
    const response = await fetch("/api/memory");
    if (!response.ok) throw new Error("Gagal memuat memori");
    const data = await response.json();
    STATE.longTerm = normalizeMemory(data);
  } catch (error) {
    setStatus("Memori lokal tidak bisa dimuat. Menggunakan memori sementara.");
  }
}

async function saveMemory() {
  try {
    await fetch("/api/memory", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(STATE.longTerm),
    });
  } catch (error) {
    setStatus("Memori lokal belum tersimpan.");
  }
}

async function sendToModel(prompt, userMessage, maxTokens) {
  setStatus("Mengirim ke model lokal...");
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      prompt,
      message: userMessage,
      max_tokens: maxTokens,
      temperature: 0.7,
      stop: ["USER:", "SYSTEM:"],
    }),
  });

  if (!response.ok) {
    throw new Error("Model lokal tidak merespons.");
  }

  const data = await response.json();
  return data.reply;
}

function updateEmotionPattern(score) {
  const bucket = score > 0 ? "positive" : score < 0 ? "negative" : "neutral";
  STATE.longTerm.emotion_patterns[bucket] = (STATE.longTerm.emotion_patterns[bucket] || 0) + 1;
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = userInput.value.trim();
  if (!input) return;

  setExpression("talk");
  resetSleepTimer();

  appendMessage("user", input);
  STATE.shortTerm.push({ role: "USER", text: input });
  STATE.shortTerm = STATE.shortTerm.slice(-10);
  STATE.interactionCount += 1;

  const analysis = analyzeInput(input);
  if (analysis.shouldRemember) {
    updateLongTermMemory(input);
  }

  STATE.longTerm.summary = summarizeShortTerm();
  STATE.longTerm.last_updated = new Date().toISOString();

  try {
    const prompt = buildPrompt(analysis);
    const reply = await sendToModel(prompt, input, analysis.maxTokens);
    appendMessage("ai", reply);
    STATE.shortTerm.push({ role: "ASSISTANT", text: reply });
    STATE.shortTerm = STATE.shortTerm.slice(-10);

    const replySentiment = sentimentScore(reply);
    updateEmotionPattern(replySentiment);

    if (replySentiment > 0) {
      setExpression("happy");
    } else if (replySentiment < 0) {
      setExpression("sad");
    } else {
      setExpression("idle");
    }

    await saveMemory();
    setStatus("Siap.");
  } catch (error) {
    appendMessage("ai", "Aku belum bisa menjangkau model lokal. Pastikan server inference berjalan.");
    setExpression("idle");
    setStatus("Model lokal belum siap.");
  }

  userInput.value = "";
  resetSleepTimer();
});

userInput.addEventListener("input", () => {
  setExpression("talk");
  resetSleepTimer();
});

window.addEventListener("load", async () => {
  await loadMemory();
  setExpression("idle");
  resetSleepTimer();
});
