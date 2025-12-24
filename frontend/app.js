const textEl = document.getElementById("text");
const scanBtn = document.getElementById("scanBtn");
const clearBtn = document.getElementById("clearBtn");
const statusEl = document.getElementById("status");
const predictionsEl = document.getElementById("predictions");
const apiUrlEl = document.getElementById("apiUrl");

function setStatus(msg) {
  statusEl.textContent = msg || "";
}

function renderPredictions(preds) {
  predictionsEl.innerHTML = "";
  if (!preds || preds.length === 0) {
    predictionsEl.innerHTML = `<div class="status">No predictions returned.</div>`;
    return;
  }

  preds.forEach(p => {
    const pct = Math.max(0, Math.min(100, (p.score || 0) * 100));
    const div = document.createElement("div");
    div.className = "pred";
    div.innerHTML = `
      <div style="flex:1; padding-right: 12px;">
        <div class="badge">${p.label}</div>
        <div class="barWrap"><div class="bar" style="width:${pct.toFixed(1)}%"></div></div>
      </div>
      <div class="score">${(p.score || 0).toFixed(4)}</div>
    `;
    predictionsEl.appendChild(div);
  });
}

async function analyze() {
  const apiBase = (apiUrlEl.value || "").trim().replace(/\/$/, "");
  const text = (textEl.value || "").trim();

  if (!apiBase) {
    setStatus("Set your API URL first.");
    return;
  }
  if (!text) {
    setStatus("Paste some text first.");
    return;
  }

  setStatus("Scanning…");
  renderPredictions([]);

  try {
    const res = await fetch(`${apiBase}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`HTTP ${res.status}: ${errText}`);
    }

    const data = await res.json();
    renderPredictions(data.predictions);
    setStatus("Done.");
  } catch (e) {
    console.error(e);
    setStatus(`Error: ${e.message}`);

    // common local dev issue: CORS
    if (String(e.message).includes("Failed to fetch")) {
      setStatus("Error: Failed to fetch. If backend is running, you likely need CORS enabled in FastAPI.");
    }
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
