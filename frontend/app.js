const API_BASE = "https://ra-galindo-cyber-threat-analyzer-api.hf.space";

const textEl = document.getElementById("text");
const scanBtn = document.getElementById("scanBtn");
const clearBtn = document.getElementById("clearBtn");
const statusEl = document.getElementById("status");
const predictionsEl = document.getElementById("predictions");

function setStatus(msg) {
  statusEl.textContent = msg || "";
}

function renderPredictions(preds) {
  predictionsEl.innerHTML = "";

  if (!Array.isArray(preds) || preds.length === 0) {
    predictionsEl.innerHTML = `<div class="status">No predictions returned.</div>`;
    return;
  }

  preds.forEach(p => {
    const pct = Math.max(0, Math.min(100, (p.score || 0) * 100));

    const div = document.createElement("div");
    div.className = "pred";

    div.innerHTML = `
      <div class="predRow">
        <span class="badge">${p.label}</span>
        <span class="score">${pct.toFixed(2)}%</span>
      </div>
      <div class="barWrap">
        <div class="bar" style="width:${pct}%"></div>
      </div>
    `;

    predictionsEl.appendChild(div);
  });
}

async function analyze() {
  const text = textEl.value.trim();

  if (!text) {
    setStatus("Please paste some text to analyze.");
    return;
  }

  setStatus("Analyzing threat patterns…");
  predictionsEl.innerHTML = "";

  try {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    if (!res.ok) {
      throw new Error(`Backend error (${res.status})`);
    }

    const data = await res.json();
    renderPredictions(data.predictions);
    setStatus("Analysis complete.");
  } catch (err) {
    console.error(err);
    setStatus("Failed to analyze text. Backend may be unavailable.");
  }
}

scanBtn.addEventListener("click", analyze);

clearBtn.addEventListener("click", () => {
  textEl.value = "";
  predictionsEl.innerHTML = "";
  setStatus("");
});

textEl.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    analyze();
  }
});
