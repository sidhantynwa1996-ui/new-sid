// Live Stock Tracker — tiny dependency-free Node server.
//
// It serves the static frontend from ./public and proxies a handful of
// Yahoo Finance endpoints. The proxy exists so the browser never has to make
// cross-origin calls to Yahoo directly (which it would be blocked from doing
// by CORS), and so the upstream URLs / headers live in one place.

import http from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";
import { dirname } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PUBLIC_DIR = join(__dirname, "public");
const PORT = process.env.PORT || 3000;

// Yahoo's public endpoints want a browser-ish User-Agent or they 403/return junk.
const UPSTREAM_HEADERS = {
  "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
  Accept: "application/json,text/plain,*/*",
};

// If the environment routes outbound HTTPS through a proxy (some sandboxes do),
// honour it. undici ships with Node, so this needs no install. On a normal
// machine HTTPS_PROXY is unset and fetch goes out directly.
let dispatcher;
const proxyUrl = process.env.HTTPS_PROXY || process.env.https_proxy;
if (proxyUrl) {
  try {
    const { ProxyAgent } = await import("undici");
    dispatcher = new ProxyAgent(proxyUrl);
  } catch {
    /* fall back to direct fetch */
  }
}

async function fetchUpstream(url) {
  const opts = { headers: UPSTREAM_HEADERS };
  if (dispatcher) opts.dispatcher = dispatcher;
  const res = await fetch(url, opts);
  if (!res.ok) {
    const err = new Error(`Upstream responded ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return res.json();
}

function sendJSON(res, status, body) {
  const data = JSON.stringify(body);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
  });
  res.end(data);
}

// --- API handlers -----------------------------------------------------------

// Symbol search / autocomplete: "apple" -> AAPL, etc.
async function handleSearch(res, query) {
  const q = (query.get("q") || "").trim();
  if (!q) return sendJSON(res, 200, { results: [] });
  const url =
    "https://query2.finance.yahoo.com/v1/finance/search?quotesCount=8&newsCount=0&q=" +
    encodeURIComponent(q);
  try {
    const data = await fetchUpstream(url);
    const results = (data.quotes || [])
      .filter((it) => it.symbol)
      .map((it) => ({
        symbol: it.symbol,
        name: it.shortname || it.longname || it.symbol,
        exchange: it.exchDisp || it.exchange || "",
        type: it.quoteType || it.typeDisp || "",
      }));
    sendJSON(res, 200, { results });
  } catch (err) {
    sendJSON(res, err.status || 502, { error: "search_failed", detail: err.message });
  }
}

// Live quote + intraday history for one symbol, derived from the chart endpoint.
async function handleQuote(res, query) {
  const symbol = (query.get("symbol") || "").trim().toUpperCase();
  if (!symbol) return sendJSON(res, 400, { error: "missing_symbol" });

  const range = query.get("range") || "1d";
  const interval = query.get("interval") || (range === "1d" ? "1m" : "5m");
  const url =
    `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}` +
    `?range=${encodeURIComponent(range)}&interval=${encodeURIComponent(interval)}&includePrePost=false`;

  try {
    const data = await fetchUpstream(url);
    const result = data?.chart?.result?.[0];
    if (!result) {
      return sendJSON(res, 404, { error: "not_found", detail: "No data for symbol" });
    }
    const meta = result.meta || {};
    const timestamps = result.timestamp || [];
    const closes = result.indicators?.quote?.[0]?.close || [];

    // Build clean [{t, p}] points, dropping any null gaps Yahoo leaves in.
    const points = [];
    for (let i = 0; i < timestamps.length; i++) {
      const p = closes[i];
      if (p != null) points.push({ t: timestamps[i] * 1000, p });
    }

    const price = meta.regularMarketPrice ?? (points.at(-1)?.p ?? null);
    const prevClose = meta.chartPreviousClose ?? meta.previousClose ?? null;
    const change = price != null && prevClose != null ? price - prevClose : null;
    const changePct = change != null && prevClose ? (change / prevClose) * 100 : null;

    sendJSON(res, 200, {
      symbol: meta.symbol || symbol,
      name: meta.longName || meta.shortName || symbol,
      currency: meta.currency || "USD",
      exchange: meta.fullExchangeName || meta.exchangeName || "",
      marketState: meta.marketState || "",
      price,
      prevClose,
      change,
      changePct,
      dayHigh: meta.regularMarketDayHigh ?? null,
      dayLow: meta.regularMarketDayLow ?? null,
      open: meta.regularMarketOpen ?? (points[0]?.p ?? null),
      volume: meta.regularMarketVolume ?? null,
      time: (meta.regularMarketTime ? meta.regularMarketTime * 1000 : Date.now()),
      points,
    });
  } catch (err) {
    sendJSON(res, err.status || 502, { error: "quote_failed", detail: err.message });
  }
}

// --- Static file serving ----------------------------------------------------

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".json": "application/json; charset=utf-8",
};

async function serveStatic(res, pathname) {
  // Resolve safely within PUBLIC_DIR (no path traversal).
  const rel = normalize(pathname === "/" ? "/index.html" : pathname).replace(/^(\.\.[/\\])+/, "");
  const filePath = join(PUBLIC_DIR, rel);
  if (!filePath.startsWith(PUBLIC_DIR)) {
    res.writeHead(403);
    return res.end("Forbidden");
  }
  try {
    const file = await readFile(filePath);
    res.writeHead(200, { "Content-Type": MIME[extname(filePath)] || "application/octet-stream" });
    res.end(file);
  } catch {
    res.writeHead(404, { "Content-Type": "text/plain" });
    res.end("Not found");
  }
}

// --- Router -----------------------------------------------------------------

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  if (url.pathname === "/api/search") return handleSearch(res, url.searchParams);
  if (url.pathname === "/api/quote") return handleQuote(res, url.searchParams);
  return serveStatic(res, url.pathname);
});

server.listen(PORT, () => {
  console.log(`\n  Live Stock Tracker running:  http://localhost:${PORT}\n`);
});
