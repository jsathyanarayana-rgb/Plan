// --- Theme handling (system/dark/light) ---
const select = document.getElementById("theme-select");
const root = document.documentElement;

function applyTheme(mode) {
  if (mode === "system") {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    root.classList.toggle("dark", prefersDark);
  } else {
    root.classList.toggle("dark", mode === "dark");
  }
}

select.addEventListener("change", () => {
  localStorage.setItem("planit-theme", select.value);
  applyTheme(select.value);
});

// initial theme
select.value = localStorage.getItem("planit-theme") || "system";
applyTheme(select.value);

// --- Chat logic ---
const chat = document.getElementById("chat");
const promptEl = document.getElementById("prompt");
const sendBtn = document.getElementById("send");

function addMsg({ role, text, loading=false }) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}${loading ? " loading" : ""}`;

  const avatar = document.createElement("div");
  avatar.className = `avatar ${role}`;
  avatar.textContent = role === "bot" ? "AI" : "You";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  chat.appendChild(wrap);
  chat.scrollTop = chat.scrollHeight;
  return wrap;
}

function updateMsg(el, text) {
  el.querySelector(".bubble").textContent = text;
  el.classList.remove("loading");
}

async function sendMessage() {
  const message = promptEl.value.trim();
  if (!message) return;

  // user bubble
  addMsg({ role: "user", text: message });
  promptEl.value = "";
  autoGrow(promptEl);

  // placeholder bot bubble (loading)
  const loadingEl = addMsg({ role: "bot", text: "Thinking", loading: true });

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    });

    const data = await res.json();
    if (res.ok && data.reply) {
      updateMsg(loadingEl, data.reply);
    } else {
      updateMsg(loadingEl, `Error: ${data.error || "Unknown error"}`);
    }
  } catch (e) {
    updateMsg(loadingEl, "Network error. Is the server running?");
  }
}

sendBtn.addEventListener("click", sendMessage);

// Enter sends, Shift+Enter adds newline
promptEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// auto-grow textarea
function autoGrow(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 200) + "px";
}
promptEl.addEventListener("input", () => autoGrow(promptEl));
autoGrow(promptEl);

// greet message (optional)
addMsg({ role: "bot", text: "Hi! I’m PlanIt. Ask me anything about careers, colleges, or study plans." });
