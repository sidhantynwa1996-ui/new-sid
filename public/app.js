// Live Stock Tracker — frontend logic.
// Talks to the local /api proxy, renders a live price + a custom canvas chart.

const $ = (id) => document.getElementById(id);

const els = {
  input: $("searchInput"),
  suggestions: $("suggestions"),
  empty: $("empty"),
  tracker: $("tracker"),
  symbol: $("symbol"),
  name: $("name"),
  price: $("price"),
  change: $("change"),
  liveBadge: $("liveBadge"),
  marketState: $("marketState"),
  rangeRow: $("rangeRow"),
  chart: $("chart"),
  tooltip: $("tooltip"),
  stats: $("stats"),
  updated: $("updated"),
  status: $("status"),
};

const POLL_MS = 5000; // refresh cadence while tracking

const state = {
  symbol: null,
  range: "1d",
  interval: "1m",
  currency: "USD",
  lastPrice: null,
  points: [],
  pollTimer: null,
  inflight: false,
};

// ---------------------------------------------------------------------------
// Formatting helpers
// ---------------------------------------------------------------------------

function fmtPrice(v, currency = state.currency) {
  if (v == null || Number.isNaN(v)) return "—";
  try {
    return new Intl.NumberFormat(undefined, {
      style: "currency",
      currency,
      maximumFractionDigits: v < 1 ? 6 : 2,
    }).format(v);
  } catch {
    return v.toFixed(2);
  }
}

function fmtNum(v) {
  if (v == null || Number.isNaN(v)) return "—";
  return new Intl.NumberFormat().format(v);
}

function fmtTime(ts) {
  const d = new Date(ts);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function fmtDateShort(ts) {
  return new Date(ts).toLocaleDateString([], { month: "short", day: "numeric" });
}

// ---------------------------------------------------------------------------
// Search / autocomplete
// ---------------------------------------------------------------------------

let searchTimer = null;
let activeSug = -1;

els.input.addEventListener("input", () => {
  clearTimeout(searchTimer);
  const q = els.input.value.trim();
  if (!q) return hideSuggestions();
  searchTimer = setTimeout(() => runSearch(q), 220);
});

els.input.addEventListener("keydown", (e) => {
  const items = [...els.suggestions.querySelectorAll("li")];
  if (!items.length) return;
  if (e.key === "ArrowDown") {
    e.preventDefault();
    activeSug = Math.min(activeSug + 1, items.length - 1);
    paintActive(items);
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    activeSug = Math.max(activeSug - 1, 0);
    paintActive(items);
  } else if (e.key === "Enter") {
    e.preventDefault();
    const pick = items[activeSug] || items[0];
    if (pick) pick.click();
  } else if (e.key === "Escape") {
    hideSuggestions();
  }
});

function paintActive(items) {
  items.forEach((li, i) => li.classList.toggle("active", i === activeSug));
}

document.addEventListener("click", (e) => {
  if (!els.suggestions.contains(e.target) && e.target !== els.input) hideSuggestions();
});

function hideSuggestions() {
  els.suggestions.hidden = true;
  els.suggestions.innerHTML = "";
  activeSug = -1;
}

async function runSearch(q) {
  try {
    const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    renderSuggestions(data.results || []);
  } catch {
    hideSuggestions();
  }
}

function renderSuggestions(results) {
  if (!results.length) return hideSuggestions();
  els.suggestions.innerHTML = "";
  activeSug = -1;
  for (const r of results) {
    const li = document.createElement("li");
    li.innerHTML = `
      <span class="sug-main">
        <span class="sug-symbol">${escapeHtml(r.symbol)}</span>
        <span class="sug-name">${escapeHtml(r.name)}</span>
      </span>
      <span class="sug-exch">${escapeHtml(r.exchange)}</span>`;
    li.addEventListener("click", () => {
      els.input.value = r.symbol;
      hideSuggestions();
      track(r.symbol);
    });
    els.suggestions.appendChild(li);
  }
  els.suggestions.hidden = false;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );
}

// Quick-pick chips
document.querySelectorAll(".chip").forEach((chip) =>
  chip.addEventListener("click", () => {
    els.input.value = chip.dataset.symbol;
    track(chip.dataset.symbol);
  })
);

// Range buttons
els.rangeRow.querySelectorAll(".range-btn").forEach((btn) =>
  btn.addEventListener("click", () => {
    els.rangeRow.querySelectorAll(".range-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    state.range = btn.dataset.range;
    state.interval = btn.dataset.interval;
    if (state.symbol) refresh(true);
  })
);

// ---------------------------------------------------------------------------
// Tracking loop
// ---------------------------------------------------------------------------

function track(symbol) {
  state.symbol = symbol.toUpperCase();
  state.lastPrice = null;
  els.empty.hidden = true;
  els.tracker.hidden = false;
  els.symbol.textContent = state.symbol;
  els.name.textContent = "Loading…";
  setStatus("");
  refresh(true);
  startPolling();
}

function startPolling() {
  stopPolling();
  state.pollTimer = setInterval(() => {
    if (!document.hidden) refresh(false);
  }, POLL_MS);
}

function stopPolling() {
  if (state.pollTimer) clearInterval(state.pollTimer);
  state.pollTimer = null;
}

// Pause/resume the live badge with tab visibility.
document.addEventListener("visibilitychange", () => {
  const live = !document.hidden && state.symbol;
  els.liveBadge.classList.toggle("paused", !live);
  els.liveBadge.childNodes[2] && (els.liveBadge.lastChild.textContent = live ? " LIVE" : " PAUSED");
  if (live) refresh(false);
});

async function refresh(isRangeChange) {
  if (!state.symbol || state.inflight) return;
  state.inflight = true;
  try {
    const url =
      `/api/quote?symbol=${encodeURIComponent(state.symbol)}` +
      `&range=${state.range}&interval=${state.interval}`;
    const res = await fetch(url);
    const data = await res.json();
    if (!res.ok || data.error) {
      throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }
    applyQuote(data, isRangeChange);
    setStatus("");
  } catch (err) {
    setStatus(`Couldn't update: ${err.message}`, true);
  } finally {
    state.inflight = false;
  }
}

function applyQuote(data, isRangeChange) {
  state.currency = data.currency || "USD";
  state.points = data.points || [];

  els.symbol.textContent = data.symbol;
  els.name.textContent = data.name || "";
  els.marketState.textContent = data.marketState
    ? data.marketState.toLowerCase().replace("regular", "open")
    : "";

  // Price with flash on change.
  const prev = state.lastPrice;
  if (data.price != null) {
    els.price.textContent = fmtPrice(data.price);
    if (prev != null && data.price !== prev && !isRangeChange) {
      els.price.classList.remove("flash-up", "flash-down");
      void els.price.offsetWidth; // restart animation
      els.price.classList.add(data.price > prev ? "flash-up" : "flash-down");
    }
    state.lastPrice = data.price;
  }

  // Change vs previous close.
  const up = (data.change ?? 0) >= 0;
  els.change.className = "change " + (up ? "up" : "down");
  if (data.change != null && data.changePct != null) {
    const sign = up ? "+" : "−";
    els.change.textContent =
      `${sign}${fmtPrice(Math.abs(data.change))} (${sign}${Math.abs(data.changePct).toFixed(2)}%)`;
  } else {
    els.change.textContent = "";
  }

  renderStats(data);

  els.updated.textContent = "Updated " + fmtTime(data.time || Date.now());
  drawChart();
}

function renderStats(d) {
  const rows = [
    ["Open", fmtPrice(d.open)],
    ["Prev Close", fmtPrice(d.prevClose)],
    ["Day High", fmtPrice(d.dayHigh)],
    ["Day Low", fmtPrice(d.dayLow)],
    ["Volume", fmtNum(d.volume)],
    ["Exchange", d.exchange || "—"],
  ];
  els.stats.innerHTML = rows
    .map(
      ([label, value]) =>
        `<div class="stat"><div class="label">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div></div>`
    )
    .join("");
}

function setStatus(msg, isError = false) {
  els.status.textContent = msg;
  els.status.className = "status" + (isError ? " error" : "");
}

// ---------------------------------------------------------------------------
// Custom canvas chart (gradient area + line + hover crosshair)
// ---------------------------------------------------------------------------

const ctx = els.chart.getContext("2d");
let chartGeom = null; // saved geometry for hover hit-testing

function drawChart() {
  const pts = state.points;
  const wrap = els.chart.parentElement;
  const dpr = window.devicePixelRatio || 1;
  const W = wrap.clientWidth;
  const H = wrap.clientHeight;
  els.chart.width = W * dpr;
  els.chart.height = H * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, W, H);

  if (pts.length < 2) {
    ctx.fillStyle = "#8a95a8";
    ctx.font = "14px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("Not enough data to chart", W / 2, H / 2);
    chartGeom = null;
    return;
  }

  const padL = 8, padR = 56, padT = 12, padB = 24;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;

  const prices = pts.map((p) => p.p);
  let min = Math.min(...prices);
  let max = Math.max(...prices);
  if (min === max) { min -= 1; max += 1; }
  const pad = (max - min) * 0.08;
  min -= pad; max += pad;

  const xOf = (i) => padL + (i / (pts.length - 1)) * plotW;
  const yOf = (p) => padT + (1 - (p - min) / (max - min)) * plotH;

  // Color by overall direction across the visible window.
  const rising = prices[prices.length - 1] >= prices[0];
  const line = rising ? "#21c87a" : "#ff5d6c";
  const fill = rising ? "rgba(33,200,122,0.18)" : "rgba(255,93,108,0.16)";

  // Horizontal gridlines + price axis labels.
  ctx.strokeStyle = "rgba(255,255,255,0.05)";
  ctx.fillStyle = "#8a95a8";
  ctx.font = "11px sans-serif";
  ctx.textAlign = "left";
  ctx.lineWidth = 1;
  const ticks = 4;
  for (let i = 0; i <= ticks; i++) {
    const val = min + (i / ticks) * (max - min);
    const y = yOf(val);
    ctx.beginPath();
    ctx.moveTo(padL, y);
    ctx.lineTo(padL + plotW, y);
    ctx.stroke();
    ctx.fillText(fmtPrice(val), padL + plotW + 6, y + 4);
  }

  // Time axis labels (start / middle / end).
  ctx.textAlign = "center";
  const labelIdx = [0, Math.floor((pts.length - 1) / 2), pts.length - 1];
  const intraday = state.range === "1d";
  for (const i of labelIdx) {
    const t = pts[i].t;
    ctx.fillText(intraday ? fmtTime(t) : fmtDateShort(t), xOf(i), H - 6);
  }

  // Area fill.
  const grad = ctx.createLinearGradient(0, padT, 0, padT + plotH);
  grad.addColorStop(0, fill);
  grad.addColorStop(1, "rgba(0,0,0,0)");
  ctx.beginPath();
  ctx.moveTo(xOf(0), yOf(prices[0]));
  for (let i = 1; i < pts.length; i++) ctx.lineTo(xOf(i), yOf(prices[i]));
  ctx.lineTo(xOf(pts.length - 1), padT + plotH);
  ctx.lineTo(xOf(0), padT + plotH);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  // Line.
  ctx.beginPath();
  ctx.moveTo(xOf(0), yOf(prices[0]));
  for (let i = 1; i < pts.length; i++) ctx.lineTo(xOf(i), yOf(prices[i]));
  ctx.strokeStyle = line;
  ctx.lineWidth = 2;
  ctx.lineJoin = "round";
  ctx.stroke();

  // Last-point marker.
  const lastX = xOf(pts.length - 1), lastY = yOf(prices[prices.length - 1]);
  ctx.beginPath();
  ctx.arc(lastX, lastY, 3.5, 0, Math.PI * 2);
  ctx.fillStyle = line;
  ctx.fill();

  chartGeom = { pts, xOf, yOf, padL, padR, plotW, W, H, line, min, max };
}

// Hover crosshair + tooltip.
els.chart.addEventListener("mousemove", (e) => {
  if (!chartGeom) return;
  const rect = els.chart.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const { pts, xOf, yOf, padL, plotW } = chartGeom;
  let i = Math.round(((x - padL) / plotW) * (pts.length - 1));
  i = Math.max(0, Math.min(pts.length - 1, i));
  drawChart();
  const px = xOf(i), py = yOf(pts[i].p);
  ctx.strokeStyle = "rgba(255,255,255,0.25)";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(px, 12);
  ctx.lineTo(px, chartGeom.H - 24);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(px, py, 4, 0, Math.PI * 2);
  ctx.fillStyle = "#fff";
  ctx.fill();

  const t = pts[i].t;
  els.tooltip.hidden = false;
  els.tooltip.style.left = px + "px";
  els.tooltip.style.top = py + "px";
  els.tooltip.innerHTML =
    `<div class="tt-price">${fmtPrice(pts[i].p)}</div>` +
    `<div class="tt-time">${state.range === "1d" ? fmtTime(t) : fmtDateShort(t) + " " + fmtTime(t)}</div>`;
});

els.chart.addEventListener("mouseleave", () => {
  els.tooltip.hidden = true;
  drawChart();
});

window.addEventListener("resize", () => state.symbol && drawChart());

// Support deep-linking via ?symbol=AAPL
const initial = new URLSearchParams(location.search).get("symbol");
if (initial) {
  els.input.value = initial;
  track(initial);
}
