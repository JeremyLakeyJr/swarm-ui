/* =============================================================
   Swarm UI – Main application JavaScript
   ============================================================= */

(function () {
  "use strict";

  const API = "";

  // ---- Tab switching ----
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document
        .querySelectorAll(".tab-btn")
        .forEach((b) => b.classList.remove("active"));
      document
        .querySelectorAll(".panel")
        .forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      const target = document.getElementById("panel-" + btn.dataset.panel);
      if (target) target.classList.add("active");
    });
  });

  // ---- Health check / status dots ----
  async function refreshHealth() {
    try {
      const res = await fetch(API + "/api/health");
      const data = await res.json();
      setDot("dotOllama", data.services.ollama === "connected");
      setDot("dotHA", data.services.homeassistant === "connected");
      setDot("dotOC", data.services.openclaw === "connected");
      setDot("dotAF", data.services.agent_framework === "available");
    } catch {
      setDot("dotOllama", false);
      setDot("dotHA", false);
      setDot("dotOC", false);
      setDot("dotAF", false);
    }
  }

  function setDot(id, ok) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.toggle("ok", ok);
    el.classList.toggle("err", !ok);
  }

  refreshHealth();
  setInterval(refreshHealth, 30000);

  // ---- Chat ----
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const chatMessages = document.getElementById("chatMessages");
  const conversationHistory = [];

  function addBubble(role, text) {
    const div = document.createElement("div");
    div.className = "chat-bubble " + role;
    div.textContent = text;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div;
  }

  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;
    chatInput.value = "";

    conversationHistory.push({ role: "user", content: text });
    addBubble("user", text);

    const bubble = addBubble("assistant", "…");

    try {
      const res = await fetch(API + "/api/chat/completions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: conversationHistory }),
      });
      const data = await res.json();
      const reply = data.message?.content || "(no response)";
      bubble.textContent = reply;
      conversationHistory.push({ role: "assistant", content: reply });
    } catch (err) {
      bubble.textContent = "Error: " + err.message;
    }
  });

  // ---- Agents ----
  const agentForm = document.getElementById("agentForm");
  const agentResult = document.getElementById("agentResult");

  agentForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const prompt = document.getElementById("agentPrompt").value.trim();
    if (!prompt) return;
    const maxRounds = parseInt(
      document.getElementById("agentRounds").value,
      10
    );
    agentResult.textContent = "Running…";

    try {
      const res = await fetch(API + "/api/agents/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, max_rounds: maxRounds }),
      });
      const data = await res.json();
      if (data.success) {
        agentResult.textContent = data.summary || JSON.stringify(data.messages, null, 2);
      } else {
        agentResult.textContent = "Error: " + (data.error || "unknown");
      }
    } catch (err) {
      agentResult.textContent = "Error: " + err.message;
    }
  });

  // ---- Home Assistant ----
  const haRefresh = document.getElementById("haRefresh");
  const haEntities = document.getElementById("haEntities");

  async function loadHAStates() {
    haEntities.innerHTML = "<p>Loading…</p>";
    try {
      const res = await fetch(API + "/api/homeassistant/states");
      const states = await res.json();
      haEntities.innerHTML = "";
      if (!Array.isArray(states) || states.length === 0) {
        haEntities.innerHTML = "<p>No entities found.</p>";
        return;
      }
      states.slice(0, 50).forEach((entity) => {
        const card = document.createElement("div");
        card.className = "entity-card";
        card.innerHTML =
          '<div class="entity-name">' + escapeHtml(entity.entity_id || "") + "</div>" +
          '<div class="entity-state">' + escapeHtml(entity.state || "unknown") + "</div>";
        haEntities.appendChild(card);
      });
    } catch (err) {
      haEntities.innerHTML = "<p>Error: " + escapeHtml(err.message) + "</p>";
    }
  }

  haRefresh.addEventListener("click", loadHAStates);

  // ---- OpenClaw ----
  const ocRefresh = document.getElementById("ocRefresh");
  const ocPipelines = document.getElementById("ocPipelines");

  async function loadPipelines() {
    ocPipelines.innerHTML = "<p>Loading…</p>";
    try {
      const res = await fetch(API + "/api/openclaw/pipelines");
      const pipelines = await res.json();
      ocPipelines.innerHTML = "";
      if (!Array.isArray(pipelines) || pipelines.length === 0) {
        ocPipelines.innerHTML = "<p>No pipelines found.</p>";
        return;
      }
      pipelines.forEach((p) => {
        const card = document.createElement("div");
        card.className = "pipeline-card";
        card.innerHTML =
          '<div class="pipeline-name">' + escapeHtml(p.name || p.id || "") + "</div>" +
          '<div class="pipeline-id">' + escapeHtml(p.id || "") + "</div>";
        ocPipelines.appendChild(card);
      });
    } catch (err) {
      ocPipelines.innerHTML = "<p>Error: " + escapeHtml(err.message) + "</p>";
    }
  }

  ocRefresh.addEventListener("click", loadPipelines);

  // ---- Agent Framework ----
  const afForm = document.getElementById("afForm");
  const afResult = document.getElementById("afResult");

  afForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const prompt = document.getElementById("afPrompt").value.trim();
    if (!prompt) return;
    const agentName = document.getElementById("afAgentName").value.trim() || "swarm_agent";
    const instructions = document.getElementById("afInstructions").value.trim();
    afResult.textContent = "Running…";

    try {
      const res = await fetch(API + "/api/agent-framework/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, agent_name: agentName, instructions }),
      });
      const data = await res.json();
      if (data.success) {
        afResult.textContent = data.summary || JSON.stringify(data.messages, null, 2);
      } else {
        afResult.textContent = "Error: " + (data.error || "unknown");
      }
    } catch (err) {
      afResult.textContent = "Error: " + err.message;
    }
  });

  // ---- Helpers ----
  function escapeHtml(str) {
    const div = document.createElement("div");
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }
})();
